## ADDED Requirements

### Requirement: Nested eventless recovery remains recoverable

When an eventless anchored HTTP bridge continuation has a registered durable
operation, a non-null operation id, a durable session owner epoch, and a proven
parent response, every `ProxyResponseError` raised while admitting or streaming
its server-owned local recovery attempt MUST retain durable-recovery eligibility
for the API-level recovery loop. This includes an upstream websocket closing
before `response.completed` during the recovery attempt. A fresh request, a
request without a proven predecessor, an unregistered operation, or a session
without a durable owner fence MUST NOT gain that eligibility. The marker MUST
NOT select or exclude accounts and MUST NOT alter load-balancer rotation.

#### Scenario: Recovery websocket also drops before its first event

- **GIVEN** an anchored Codex HTTP bridge continuation with a registered durable
  operation and parent response
- **AND** the first upstream attempt returns `previous_response_not_found`
- **WHEN** the server-owned local recovery websocket closes before emitting any
  response event or `response.completed`
- **THEN** the nested `stream_incomplete` remains eligible for the API-level
  indefinite recovery loop
- **AND** the downstream Codex stream is not terminated by that nested failure

#### Scenario: Missing durable proof remains terminal

- **GIVEN** a first turn or a bridge request missing any durable operation,
  owner-epoch, or predecessor proof
- **WHEN** its upstream websocket closes eventlessly
- **THEN** the failure follows the existing terminal path and is not marked for
  indefinite recovery
