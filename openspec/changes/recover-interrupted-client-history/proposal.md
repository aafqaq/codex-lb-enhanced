# Change: Recover interrupted client history across accounts

## Why

Codex rebuilds a failed turn from its local transcript and retries with a full input history. The HTTP Responses bridge can currently mistake that authoritative resend for an ordinary continuation, inject a stale `previous_response_id`, trim hundreds of retained items to a short suffix, and pin the retry back to the account that lost continuity or quota. This defeats account failover and can permanently strand an otherwise recoverable local conversation.

## What Changes

- Recognize a validated Codex full-history retry after completed or interrupted assistant output as an account-neutral recovery source.
- Never replace a proven full-history recovery request with a stale proxy/session anchor.
- Preserve the configured account-selection policy while excluding accounts that proved exhausted during the current request.
- Replay internally only before downstream-visible model output; after visible output, use client-native retry semantics so the client resends its authoritative transcript.
- Keep tool-call, account-scoped file, hosted state, and unknown-shape replay guards fail closed.
- Adapt only the outward recovery error contract by client surface; account failover and pool exhaustion remain client-independent.

## Impact

- Affected spec: `responses-api-compat`
- Affected code: HTTP Responses bridge replay classification, stale-anchor handling, account failover, and streaming terminal adaptation
- Affected tests: replay-safety unit tests and `/backend-api/codex/responses` bridge integration regressions
- Deployment is intentionally out of scope for this change.
