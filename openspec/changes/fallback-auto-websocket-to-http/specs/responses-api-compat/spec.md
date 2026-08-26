## ADDED Requirements

### Requirement: Auto transport recovers before the first WebSocket event

When upstream transport mode is `auto` and WebSocket is selected, the proxy
MUST retry the same Responses request over HTTP if the WebSocket connection
times out, fails at the network layer, or closes before producing its first
response event. The retry MUST use the HTTP-specific payload normalization and
headers. The unsuccessful WebSocket leg MUST NOT independently make an
otherwise healthy account unavailable before the HTTP result is known.

#### Scenario: Connect timeout falls back to HTTP

- **GIVEN** `auto` mode selects upstream WebSocket
- **AND** the WebSocket connect attempt times out before any event
- **WHEN** the equivalent HTTP stream succeeds
- **THEN** the downstream receives one normal HTTP-backed response stream
- **AND** no WebSocket transport error is exposed

#### Scenario: Empty WebSocket close falls back to HTTP

- **GIVEN** the WebSocket handshake succeeds
- **AND** it closes before the first response event
- **THEN** the proxy retries the same request over HTTP

### Requirement: Auto fallback preserves replay safety and upstream errors

The proxy MUST NOT issue the HTTP fallback after any WebSocket response event
has reached the downstream. Structured upstream authentication, rate-limit,
and quota errors MUST retain their original classification. Explicit forced
WebSocket mode MUST NOT silently fall back to HTTP.

#### Scenario: Visible event prevents hidden replay

- **GIVEN** a WebSocket response event has been forwarded
- **WHEN** the connection then fails
- **THEN** the proxy does not replay the request over HTTP

#### Scenario: Forced WebSocket remains forced

- **GIVEN** upstream transport mode is explicitly `websocket`
- **WHEN** the WebSocket connection fails before its first event
- **THEN** no HTTP fallback is attempted
