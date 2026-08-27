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

### Requirement: Server-owned recovery iterators close deterministically

Every server-owned recovery attempt MUST close both its API-level attempt
iterator and underlying HTTP bridge service stream after success, failure, or
downstream cancellation. Repeated eventless recovery failures MUST NOT retain
an abandoned iterator, API-key reservation lifecycle, or bridge generator.

#### Scenario: Failed recovery is closed before its successor

- **GIVEN** a durable recovery attempt fails eventlessly and remains eligible
  for another attempt
- **WHEN** the recovery loop creates the successor attempt
- **THEN** the failed attempt iterator has already been closed
- **AND** the successor iterator is also closed after it completes

### Requirement: Received bridge frames are not mistaken for idle streams

The HTTP bridge MUST mark a matched upstream frame as activity before durable
persistence and downstream delivery. While that request's frame processing is
in progress, the downstream stream MUST NOT consume an idle-timeout strike;
the marker MUST remain request-scoped so activity from a multiplexed sibling
request cannot suppress this request's timeout.

#### Scenario: Replacement response is persisted after receipt

- **GIVEN** a pre-response recovery reconnect receives `response.created`
- **WHEN** persistence or queue delivery takes longer than one keepalive
  interval
- **THEN** the request remains pending until the received frame is delivered
- **AND** the subsequent `response.completed` event can still be matched
- **AND** no `stream_idle_timeout` terminal event is emitted for that frame.
