# Why

An anchored Codex HTTP-bridge request can enter local recovery after an
upstream `previous_response_not_found` response. If that server-owned recovery
attempt then loses its upstream websocket before emitting any response event,
the nested `ProxyResponseError` bypasses the outer bridge exception handler.
The API recovery loop therefore receives an unmarked `stream_incomplete` and
returns a broken stream to Codex even though the operation has a durable parent
and operation fence.

# What Changes

- Centralize durable-recovery eligibility marking behind the existing durable
  session, owner epoch, operation id, and predecessor proof.
- Apply the same proof to failures raised while creating or streaming the
  server-owned local recovery attempt.
- Explicitly close every server-owned recovery iterator after success,
  failure, or cancellation so repeated recovery cannot retain bridge resources.
- Treat a matched upstream frame as request activity as soon as the receive
  task completes, and defer idle-timeout accounting while that request's
  persistence/delivery work is still in progress.
- Keep fresh turns, non-durable sessions, and requests without a predecessor on
  their existing terminal error path.

# Capabilities

## Modified Capabilities

- `responses-api-compat`: eventless failures of a proven server-owned recovery
  attempt must return to the API-level indefinite recovery loop instead of
  truncating the downstream Codex stream.

# Impact

Old Codex conversations no longer lose their downstream stream solely because
the first local reattach attempt also encounters an eventless websocket drop.
Account selection and load-balancer rotation remain unchanged; this change only
preserves recovery metadata on the nested failure and releases each attempt's
resources deterministically.
