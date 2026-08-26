# Change: Fall back from unproductive auto WebSocket attempts to HTTP

## Why

The `auto` upstream transport currently falls back to HTTP only when the
WebSocket handshake returns HTTP 426. A connect timeout, network failure, or
connection close before the first response event instead aborts the turn even
though the same account and request commonly work over the Responses HTTP
stream. Operators therefore have to force HTTP globally and lose automatic
transport selection.

## What Changes

- In `auto` mode, retry the same request over HTTP when the WebSocket cannot
  connect or closes before its first response event.
- Preserve structured authentication, rate-limit, quota, and other upstream
  response semantics instead of hiding them behind transport fallback.
- Never replay over HTTP after a WebSocket event has reached the downstream
  client, preventing duplicate text and tool calls.
- Keep forced WebSocket mode fail-fast.
- Defer WebSocket-leg account health penalties while an eligible HTTP fallback
  is still pending; let the final transport outcome determine health.

## Impact

- Affected code: Responses upstream transport selection and WebSocket
  lifecycle accounting.
- No schema, migration, port, or deployment change is required.
- Default `auto` mode becomes resilient without changing explicit `http` or
  `websocket` behavior.
