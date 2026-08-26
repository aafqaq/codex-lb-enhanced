# Context

Official Responses WebSocket state is connection-local. When a connection is
lost, a client can reconnect with a valid `previous_response_id`, or resend
the full conversation input when that cache entry is unavailable. This change
addresses an earlier boundary: an upstream WebSocket attempt that never
produced a response event.

Replaying after the first visible event is deliberately excluded. At that
point a text prefix or tool call may already have affected the client, so the
native Codex whole-sampling retry boundary owns recovery instead of a hidden
proxy replay.

Example: `auto` selects WebSocket, the connect attempt times out, and no event
has been emitted. The proxy immediately submits the HTTP Responses equivalent
on the same account. If HTTP completes, the client sees one normal stream and
the account remains healthy. If HTTP returns quota exhaustion, normal pool
failover handles the account-level condition.
