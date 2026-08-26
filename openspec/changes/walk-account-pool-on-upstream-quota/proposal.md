# Change: Walk the account pool on upstream quota exhaustion

## Why

A single ChatGPT account can exhaust its Codex allowance while other accounts
in the pool remain usable.  Upstream has emitted that condition both as a
structured quota code and as the message `The usage limit has been reached`.
Forwarding either form immediately defeats the load balancer and can terminate
an otherwise recoverable Codex turn.

## What Changes

- Normalize structured and message-only upstream quota exhaustion into one
  account-health condition.
- Before model output is visible, exclude each exhausted account and replay the
  request across the eligible pool, without the generic retry-count ceiling.
- Return `usage_limit_reached` only after no eligible replacement account
  remains.
- After output is visible, do not replay inside the proxy.  Persist the
  exhausted account and end the Codex transport at a private native-retry
  boundary so the official client resubmits the complete sampling request.
- Keep public OpenAI-compatible streams on their existing explicit terminal
  failure contract.

## Impact

- Affected code: raw Responses SSE, native Responses WebSocket, HTTP bridge,
  account selection, and stream normalization.
- Existing continuity ownership, API-key reservations, tool-call deduplication,
  public `/v1` contracts, and non-quota error handling remain intact.
- No database migration is required.
