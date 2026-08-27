## ADDED Requirements

### Requirement: Authoritative full-history retries recover interrupted turns

When a client retries an interrupted HTTP Responses turn with list-shaped full history and no client-supplied `previous_response_id`, the service MUST treat that history as the recovery authority after the existing retained-prefix and account-neutral replay proof succeeds. A completed portable assistant output with phase `commentary` MAY establish the retained boundary when no tool call remains pending and the following user and transparent developer messages belong to the same nonblank client turn. Codex client metadata containing only `turn_id` plus optional numeric `create_time` and string-list `content_item_kinds` is account-neutral; cross-account dispatch MUST reduce it to `turn_id`. The service MUST preserve portable assistant, user, developer, and paired direct-tool history in order.

The service MUST NOT replace a proven authoritative full-history retry with a stale durable or session-level previous-response anchor. If an optimization first submits an anchored trimmed suffix and upstream rejects that anchor, the service MUST retry the validated unanchored full history before surfacing failure, provided no model output became downstream-visible. The failed continuity owner MUST be excluded only for the current failover when account-scoped failure requires exclusion, and replacement selection MUST continue through the configured load-balancer policy.

#### Scenario: Interrupted Codex commentary is resent as full history

- **GIVEN** a completed retained assistant commentary message has portable output and no pending tool call
- **AND** the client appends one user message and one transparent developer message with the same nonblank turn ID
- **WHEN** the prior upstream continuation is unavailable
- **THEN** the bridge validates and submits the complete projected history without the stale previous-response anchor
- **AND** account selection remains governed by the configured routing policy

#### Scenario: Stale anchor rejects a trimmed request

- **GIVEN** the proxy retained a validated unanchored full-history body before injecting and trimming an owner-bound anchor
- **WHEN** upstream reports `previous_response_not_found` before downstream-visible model output
- **THEN** the bridge clears the anchor and stale affinity, excludes the failed owner when the failure is account-scoped, and retries the validated full body
- **AND** it does not ask the client to repeat the same stale anchored attempt

#### Scenario: Quota owner is exhausted before output

- **WHEN** an account reports an upstream usage-limit terminal before downstream-visible model output
- **THEN** the bridge records the account-scoped quota state, excludes that account for the request, and tries the next eligible account
- **AND** it returns the upstream quota terminal only after the eligible pool is exhausted

#### Scenario: Paused sticky owner does not create an unbounded wait

- **GIVEN** a request is routed through a hard sticky session whose owner was manually paused or otherwise became unavailable
- **WHEN** account selection returns `hard_affinity_saturated`
- **THEN** the service makes at most one bounded recovery attempt instead of waiting until the request budget expires
- **AND** a request with a verified account-neutral full replay clears the stale affinity and continues through the configured load-balancer policy
- **AND** a request without a safe replay receives `previous_response_owner_unavailable` (or the protocol-equivalent upstream-unavailable contract) with a request log entry
- **AND** no other client, websocket, or account-rotation policy is changed by this recovery path

### Requirement: Partial-output recovery remains client-authored

The service MUST NOT replay a generation internally on another account after model output has become downstream-visible. It MUST instead emit the retryable recovery contract appropriate to the client surface. For Codex Responses traffic, that contract MUST cause the official client to rebuild the turn from local history and retry without relying on the failed account's `previous_response_id`. The next proven full-history retry MUST bypass the invalid anchor. Other clients MUST receive their protocol-compatible retryable error without changing account health, pool walking, or load-balancer policy.

#### Scenario: Account exhausts after visible output

- **WHEN** upstream reports usage exhaustion after text, reasoning, or a tool call became downstream-visible
- **THEN** the bridge does not splice a second account's generation into the active stream
- **AND** Codex receives retryable stream semantics and can resend its full local transcript
- **AND** the resent transcript is not re-anchored to the exhausted account

#### Scenario: Unsafe full history fails closed

- **GIVEN** the resent history contains unmatched tool state, account-scoped files, opaque hosted state, malformed metadata, unknown shapes, or an unverified retained prefix
- **WHEN** cross-account recovery is evaluated
- **THEN** the service does not dispatch that state to another account
- **AND** it returns the client-surface recovery/error contract instead of silently dropping context
