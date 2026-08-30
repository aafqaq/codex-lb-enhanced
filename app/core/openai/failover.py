"""Request-scoped OpenAI failover state.

This module intentionally contains no account-selection or transport code.  It
is the small state machine shared by HTTP, WebSocket, compact, and bridge
adapters.  The load balancer still decides *which* eligible account is next;
this object only records accounts already attempted by the current request and
the bounded same-account retry policy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class OpenAIFailureClass(StrEnum):
    """Failure classes understood by the request failover state machine."""

    QUOTA_EXHAUSTED = "quota_exhausted"
    RATE_LIMITED = "rate_limited"
    UPSTREAM_TRANSPORT = "upstream_transport"
    UPSTREAM_TIMEOUT = "upstream_timeout"
    UPSTREAM_PROTOCOL = "upstream_protocol"
    AUTHENTICATION = "authentication"
    MODEL_UNSUPPORTED = "model_unsupported"
    CAPACITY = "capacity"
    CLIENT_CANCELLED = "client_cancelled"
    UNKNOWN = "unknown"


class OpenAIFailoverAction(StrEnum):
    """Decision returned after recording one upstream failure."""

    RETRY_SAME_ACCOUNT = "retry_same_account"
    TRY_NEXT_ACCOUNT = "try_next_account"
    TERMINAL = "terminal"


@dataclass(frozen=True, slots=True)
class OpenAIFailure:
    """A normalized failure from any OpenAI transport adapter."""

    failure_class: OpenAIFailureClass
    code: str
    message: str
    status_code: int | None = None
    retry_next_account: bool = True
    retry_same_account: bool = False
    account_health_penalty: bool = True
    safe_full_replay: bool = False


@dataclass(slots=True)
class OpenAIFailoverState:
    """Sub2API-style per-request failover state.

    ``failed_account_ids`` is deliberately independent of durable affinity.
    Callers pass it to their normal account selector on every iteration.  A
    sticky/continuity hint may improve the first selection, but once an account
    is here it can never be returned by the replacement selection for this
    request.
    """

    max_switches: int
    failed_account_ids: set[str] = field(default_factory=set)
    same_account_retry_counts: dict[str, int] = field(default_factory=dict)
    switch_count: int = 0
    last_failure: OpenAIFailure | None = None

    def __post_init__(self) -> None:
        # Callers derive this value from several runtime settings.  Keep the
        # state machine total even when an unset/negative value slips through:
        # at least one replacement decision is always meaningful, while a
        # quota walk can still continue past this ordinary transport budget.
        self.max_switches = max(int(self.max_switches), 1)

    def is_excluded(self, account_id: str) -> bool:
        return account_id in self.failed_account_ids

    def same_account_retry_allowed(self, account_id: str, limit: int) -> bool:
        """Reserve one bounded retry on the same account."""

        if limit <= 0:
            return False
        count = self.same_account_retry_counts.get(account_id, 0)
        if count >= limit:
            return False
        self.same_account_retry_counts[account_id] = count + 1
        return True

    def exclude_account(self, account_id: str, failure: OpenAIFailure) -> bool:
        """Exclude an account and advance the switch budget.

        Returns ``True`` when another account may be attempted.  Adding an
        account is idempotent, so duplicated transport/usage signals cannot
        consume multiple switch slots or cause A->B->A routing.
        """

        if not account_id:
            return False
        self.last_failure = failure
        quota_walk = failure.failure_class is OpenAIFailureClass.QUOTA_EXHAUSTED
        if account_id in self.failed_account_ids:
            return failure.retry_next_account and (quota_walk or self.switch_count < self.max_switches)
        self.failed_account_ids.add(account_id)
        if not failure.retry_next_account:
            return False
        # Quota exhaustion is scoped to one account.  It must walk the finite
        # selector pool even when the ordinary transport retry budget (often
        # three attempts) has already been consumed.
        if self.switch_count >= self.max_switches and not quota_walk:
            return False
        self.switch_count += 1
        return True

    def exclude_account_id(
        self,
        account_id: str,
        *,
        failure_class: OpenAIFailureClass = OpenAIFailureClass.UNKNOWN,
        code: str = "upstream_error",
        message: str = "Upstream account failed",
        status_code: int | None = None,
        retry_next_account: bool = True,
        retry_same_account: bool = False,
        safe_full_replay: bool = False,
    ) -> bool:
        """Convenience boundary used by transport adapters.

        Adapters only know the wire classification fields.  Constructing the
        immutable failure here keeps all switch-budget accounting in one
        place and prevents a raw ``set.add`` from bypassing the controller.
        """

        if not account_id:
            return False
        return self.exclude_account(
            account_id,
            OpenAIFailure(
                failure_class=failure_class,
                code=code,
                message=message,
                status_code=status_code,
                retry_next_account=retry_next_account,
                retry_same_account=retry_same_account,
                safe_full_replay=safe_full_replay,
            ),
        )

    def record_failure(
        self,
        account_id: str,
        failure: OpenAIFailure,
        *,
        same_account_retry_limit: int = 0,
    ) -> OpenAIFailoverAction:
        """Record a normalized failure and choose the next recovery action.

        This is the single decision boundary used by transport adapters.  A
        retry on the same account is reserved before the account is excluded;
        otherwise the account enters the request exclusion ledger and the
        normal load-balancer selector is asked for the next account.  The
        selector remains responsible for rotation order, health, model
        support, and capacity, exactly as it is for a first attempt.
        """

        self.last_failure = failure
        if failure.retry_same_account and self.same_account_retry_allowed(account_id, same_account_retry_limit):
            return OpenAIFailoverAction.RETRY_SAME_ACCOUNT
        if not failure.retry_next_account:
            return OpenAIFailoverAction.TERMINAL
        if self.exclude_account(account_id, failure):
            return OpenAIFailoverAction.TRY_NEXT_ACCOUNT
        return OpenAIFailoverAction.TERMINAL

    def exhausted(self) -> bool:
        """Whether the configured per-request switch budget is exhausted."""

        return self.switch_count >= self.max_switches

    def replacement_exclusions(self) -> frozenset[str]:
        """Immutable exclusions passed to the normal account selector."""

        return frozenset(self.failed_account_ids)

    def reset_after_success(self) -> None:
        """Start a new logical turn after a replacement account succeeds.

        The exclusion ledger is request-scoped evidence, not a permanent
        account ban.  Account health and quota reset timestamps are owned by
        the load balancer; retaining this set across later turns would make a
        recovered account unavailable forever on a warm bridge session.
        """

        self.failed_account_ids.clear()
        self.same_account_retry_counts.clear()
        self.switch_count = 0
        self.last_failure = None
