## ADDED Requirements

### Requirement: Preserve per-account quota causes through selection

The proxy account selector SHALL preserve a structured `usage_limit_reached` result
when a preferred account is exhausted, regardless of request transport or request
kind.  The selector MUST NOT replace that cause with a generic owner-unavailable
result before the transport recovery layer can evaluate replay safety.

#### Scenario: Selection-time owner quota is observable

- **WHEN** the resolved previous-response owner is marked quota-exhausted before a
  continuation is dispatched
- **THEN** selection returns `usage_limit_reached` with any available reset hint
- **AND** the request log includes the owner account and quota cause

### Requirement: Quota failover is bounded by request exclusions

When a request has a verified account-neutral full resend, the proxy SHALL exclude
each account that returns a quota terminal for that logical request and re-run the
existing load-balancer strategy.  The proxy MUST NOT select an excluded account in a
later attempt, and MUST return the pool-wide `usage_limit_reached` result only after
no eligible account remains.

#### Scenario: Multiple accounts exhaust in sequence

- **GIVEN** accounts A and B return quota exhaustion and account C is usable
- **WHEN** a pre-output request is retried
- **THEN** the proxy attempts A, then B, then C at most once each
- **AND** the client receives only the successful response from C

#### Scenario: Entire pool is exhausted

- **GIVEN** every selectable account returns quota exhaustion
- **WHEN** all account exclusions are applied
- **THEN** the proxy returns `usage_limit_reached` with the pool reset metadata
- **AND** it does not return a generic `no_accounts` or owner-unavailable error

### Requirement: Unsafe continuations remain owner-bound

The proxy SHALL NOT move a file-pinned request, opaque delta continuation, or request
that has exposed model output to another account solely because the owner is
quota-exhausted.  Such a request MUST preserve the native terminal error or the
official client-retry boundary semantics.

#### Scenario: File-pinned owner quota

- **WHEN** a file-pinned continuation's owner reaches its quota
- **THEN** no replacement account is selected
- **AND** the client receives the structured quota error
