# Change: Preserve native WebSocket continuity after delayed reconnects

## Why

An interrupted Codex turn may be retried immediately, or only after the user
returns hours or days later. An in-memory response-owner cache is insufficient
for the delayed case: the next `previous_response_id` request can no longer be
bound to the account that owns the upstream response and the conversation is
reported dead.

## What Changes

- Keep the durable request-log owner record as the source of truth for response
  IDs even when the original turn ends in `stream_incomplete`, transport loss,
  quota exhaustion, or another non-success state.
- Continue to use the in-memory owner index as a bounded hot-path cache.
- On a later reconnect, resolve the durable owner first when the cache is cold
  or stale, then apply the existing account-switch/full-context recovery rules.
- Keep tool-call replay guarded by response ownership and downstream sequence
  watermarks; delayed recovery must never duplicate an already emitted tool
  call.

## Impact

No schema migration is required because request-log ownership already persists
the response ID and account ID. This change closes the abnormal-finalization
gap in the native WebSocket path.
