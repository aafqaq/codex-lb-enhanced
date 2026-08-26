## ADDED Requirements

### Requirement: Upstream quota exhaustion consumes the eligible account pool

When an upstream account reports an allowance exhaustion code, or reports the
equivalent usage-limit message without a stable code, the proxy MUST classify
the condition as selected-account quota evidence.  Before any model output is
visible, the proxy MUST exclude that account and attempt every other eligible
account allowed by request continuity and API-key assignment.  The ordinary
transient retry-count ceiling MUST NOT stop this finite pool walk.  The proxy
MUST expose `usage_limit_reached` only when no eligible replacement remains.

#### Scenario: Message-only quota switches accounts

- **GIVEN** the selected account returns `The usage limit has been reached`
  without a stable quota code
- **AND** no model output has been forwarded
- **WHEN** another assigned account is eligible
- **THEN** the failed account is marked exhausted and excluded
- **AND** the same request is dispatched on the replacement account
- **AND** no single-account quota event reaches the client

#### Scenario: Pool exhaustion is terminal

- **GIVEN** every eligible assigned account has returned quota exhaustion for
  the request
- **WHEN** account selection has no remaining candidate
- **THEN** the client receives `usage_limit_reached`
- **AND** the error is not disguised as a generic empty-pool failure

### Requirement: Visible quota failure uses the native Codex retry boundary

After model output or a tool-call event is visible, the proxy MUST NOT replay
the request body on another account because doing so could duplicate text or
side effects.  For native Codex response routes, it MUST persist the exhausted
account, suppress that account's terminal quota frame, consume its private
control marker internally, and finish the transport without
`response.completed` or `response.failed`.  This allows the official Codex
client to perform its whole-sampling retry from local conversation history.

The public OpenAI-compatible `/v1` route MUST retain its explicit terminal
stream guard and MUST NOT expose the private control marker.

#### Scenario: Quota arrives after visible text

- **GIVEN** a native Codex request has forwarded an output-text delta
- **WHEN** the selected account reports usage-limit exhaustion
- **THEN** no quota or synthetic `stream_incomplete` event is forwarded
- **AND** the exhausted account is unavailable to the client's replacement
  request
- **AND** no proxy-local replay duplicates the visible prefix

#### Scenario: Public stream retains an explicit failure

- **GIVEN** the same post-output condition occurs on a public `/v1` stream
- **THEN** the public contract guard emits a terminal failure
- **AND** the internal native-retry marker is never forwarded
