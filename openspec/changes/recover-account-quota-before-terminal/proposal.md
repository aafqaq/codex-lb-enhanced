## Why

When one account reaches an upstream usage limit, account selection can flatten the
structured quota result into a generic owner-unavailable response.  A continuation
that already contains a verified, self-contained request can therefore fail even
though another pool account is usable.  The same loss of cause prevents operators
from distinguishing an exhausted account from a genuinely empty or unhealthy pool.

## What Changes

- Preserve the structured `usage_limit_reached` selection result for every proxy
  transport, including hard previous-response owners.
- Treat a quota-exhausted continuity owner as recoverable only when a verified,
  account-neutral full resend is available; exclude that account and continue the
  existing load-balancer strategy.
- Allow repeated pre-output quota terminals to walk the finite account pool, while
  treating `response.created` without model output as replay-safe.
- Keep file-pinned and unproven delta continuations owner-bound and fail closed with
  the native terminal error when no safe replay exists.
- Record the owner account, transport, and reset hint in structured logs before
  account-neutral recovery.

## Impact

- **Affected capabilities:** `account-routing`, `conversations-api` (stream
  continuity behavior), and `proxy-runtime-observability`.
- No new settings, migrations, ports, or container changes are required.
- Existing routing, sticky-session, file-affinity, admission, and settlement rules
  remain authoritative; recovery only changes the action taken after a confirmed
  per-account quota failure.
- A terminal `usage_limit_reached` is emitted only after the selectable pool has
  been exhausted or the request cannot be safely replayed.
