# Change: Release the dispatched-payload owner after a quota stop

## Why

The pool walk added by `walk-account-pool-on-upstream-quota` could not run for
a real Codex Desktop turn.  Before dispatching a request whose body is not
provably account-neutral, the raw Responses SSE path records the selected
account as the payload owner so a partially committed continuation cannot move
accounts.  A definitive `usage_limit_reached` response is returned before the
account accepts anything, yet the owner was still recorded, so the follow-up
selection required the very account the walk had just excluded.  Selection
answered `preferred_account_unavailable`, and the client received the exhausted
account's `429 The usage limit has been reached` while the rest of the pool was
idle.

Codex client bookkeeping such as `stream_options` and `_extra` also keeps the
strict cross-account projection from proving a first turn portable.  The
websocket and HTTP bridge transports already fall back to a permissive
projection for an unanchored client resend; the raw SSE path had no
equivalent.

## What Changes

- On a definitive quota failover, release the recorded payload owner for an
  unanchored turn and continue the pool walk with the request rebuilt in its
  portable form.  Anchored continuations and file pins stay owner-bound.
- Share one unanchored-quota-replay projection across transports so the raw
  SSE path uses the same strict-then-permissive policy as the websocket and
  HTTP bridge paths.

## Impact

- Affected code: raw Responses SSE retry path and the shared cross-account
  replay-projection policy.
- Existing continuity ownership, file pins, anchored continuations, and
  non-quota failover behavior are unchanged.
- No schema, configuration, or dependency changes.
