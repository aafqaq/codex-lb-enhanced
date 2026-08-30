# Design

## Request-scoped state

`OpenAIFailoverState` is the shared controller state and owns:

- `failed_account_ids`: accounts already attempted in this request;
- `same_account_retry_counts`: bounded retries for transient failures;
- `switch_count` and `max_switches`;
- the last classified failure;
- the last normalized failure and replay-safe decision associated with it.

The normal load-balancer strategy remains responsible for ordering and quota
selection. The controller passes the exclusion set into that strategy on every
attempt.

## State transitions

```text
SELECT -> FORWARD
FORWARD -- bounded transient retry --> FORWARD
FORWARD -- failoverable account failure --> EXCLUDE -> SELECT
FORWARD -- partial semantic output --> CLIENT_CONTINUATION or TERMINAL
SELECT -- no candidates with failures --> TERMINAL_POOL_EXHAUSTED
```

Account-owned sticky/continuity hints are preferences during `SELECT`. Once an
account enters `failed_account_ids`, those hints are detached for the next
selection. A hard upstream response owner may still be used for a safe replay,
but it cannot veto a healthy replacement when a verified full request is
available.

When the client sends only a delta with an account-scoped
`previous_response_id`, the durable HTTP-bridge operation/event spool is the
source of truth. The replay projector walks the parent-response chain,
deduplicates legacy full-resend prefixes, appends the current suffix, and
strips the old anchor before selection. If the spool is incomplete, the
request remains fail-closed rather than silently dropping context.

## Transport integration

HTTP streaming, Responses WebSocket turns, legacy compact requests, and the
HTTP bridge use the same failure classes and controller transitions. Transport
adapters only translate wire events and release leases; they do not implement
the account exclusion policy themselves. A replacement is not considered
successful until it emits a terminal completion; only then is the session
ledger reset for the next logical turn.

## Observability

Every attempt records request id, account id, attempt number, failure class,
excluded count, next-account decision, replay mode, and terminal reason. No
credentials or full request bodies are logged.
