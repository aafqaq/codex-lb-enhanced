## ADDED Requirements

### Requirement: Abnormal turns retain a durable response owner

When a native Codex response has a response ID and its stream ends without a
successful completion, the proxy MUST retain the response-ID-to-account owner
mapping in the durable request-log path before releasing the request state. A
later connection using that `previous_response_id` MUST be able to resolve the
owner even when the process-local cache is empty.

#### Scenario: Delayed reconnect after network loss

- **GIVEN** a response ID was observed before the downstream socket failed
- **AND** the user reconnects hours or days later with that ID
- **WHEN** the process-local owner cache has been evicted
- **THEN** durable owner lookup resolves the original account or a safe account
  handoff
- **AND** the request is not rejected solely because the original socket ended

### Requirement: Delayed recovery remains replay-safe

The proxy MUST preserve response and downstream sequence watermarks while
resolving a delayed owner. It MUST NOT replay a request after visible output or
duplicate a completed tool call merely because the reconnect was delayed.
