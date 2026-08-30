# Tasks

- [x] Add typed request-scoped failover state and failure classification.
- [x] Route HTTP Responses streaming retries through the controller.
- [x] Route Responses WebSocket turn retries through the controller.
- [x] Route compact and HTTP-bridge recovery through the controller.
- [x] Detach failed account affinity before every replacement selection.
- [x] Preserve canonical full replay payloads without fixed-turn truncation.
- [x] Keep normal routing strategy, API-key account scopes, and quota headers intact.
- [x] Materialize the account-neutral replay body whenever an anchor is used,
  so recovery never discovers mid-stream that it has nothing to replay.
- [x] Surface a stale anchor as a recoverable error (only when a replay body
  exists and the client has seen no semantic output) instead of ending the
  client stream, matching the official client's reset-and-resend behaviour.
- [x] Scope transport-level connect exclusions to the connect loop; only
  account-scoped verdicts enter the request failover ledger.
- [x] Translate compact's local failure labels into `OpenAIFailureClass`.
- [ ] Remove obsolete duplicate account-switch branches after call sites migrate.
- [ ] Verify on the dev server against real accounts: the unit suite proves the
  projection and gating contracts, not that upstream accepts the rebuilt body.

## Verification status

- `ruff check`, `ty check`, and the proxy architecture check pass.
- `pytest tests/unit` matches the pre-change baseline exactly (34 pre-existing
  failures on this Windows workstation: helm artifacts, sqlite path handling,
  `fork` semantics, proxy env vars; none in the changed transport code).
- `tests/unit/test_anchor_replay_materialization.py` exercises the real
  projector chain end to end, including the fail-closed cases.
