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
- [x] Verify on the dev server against real accounts.
- [x] Let a proven upstream-state owner supersede a stale sticky routing row
  instead of failing the turn closed, and repair the row so the next turn
  agrees. Mirrors sub2api, which rewrites the session binding to whichever
  account selection actually landed on
  (`openai_gateway_scheduling.go:1376`/`1415`) and never raises a conflict.
- [x] Compare HTTP-bridge session identities only inside one namespace. A live
  session without a durable id reports `live:<key>`, which can never equal a
  durable alias's `durable:<id>`, so the cross-namespace comparison failed
  healthy turns closed.
- [ ] Remove obsolete duplicate account-switch branches after call sites migrate.

## Dev-server verification (38.244.44.180, container
`codex-lb-enhanced-prod-copy`, image built from this branch, started
2026-08-30 05:53Z)

`request_logs`, per day:

| day | requests | errors | rate | `previous_response_not_found` |
| --- | --- | --- | --- | --- |
| 08-26 | 1588 | 88 | 5.5% | 62 |
| 08-27 | 2325 | 79 | 3.4% | 46 |
| 08-28 | 1395 | 11 | 0.8% | 3 |
| 08-30 (this branch) | 516 | 3 | 0.58% | **0** |

`previous_response_not_found` (110 occurrences historically, the failure this
change targets) and `stream_incomplete` (137) are both gone. The three
remaining errors were all `continuity_owner_conflict` on the compaction
surface, from a single healthy account -- the defect fixed above.

Evidence for that defect, from the same database:

- `sticky_sessions['http_turn_b89fed...'] = d553f4f6` written 08:58:52.838
- `http_bridge_session_aliases['http_turn_b89fed...']` -> session `ff5de3cc`,
  account `02a44aa5`, created 08:59:06

One turn-state token, two accounts, two stores, fourteen seconds apart. Three
compact requests 502'd at 09:07:11/13/15; the client's fourth attempt at
09:07:54 dropped the turn-state header, fell through to prompt-cache affinity,
and succeeded on `02a44aa5` -- the account the "conflict" was about.

## Verification status

- `ruff check`, `ty check`, and the proxy architecture check pass.
- `pytest tests/unit` matches the pre-change baseline exactly (34 pre-existing
  failures on this Windows workstation: helm artifacts, sqlite path handling,
  `fork` semantics, proxy env vars; none in the changed transport code).
- `tests/unit/test_anchor_replay_materialization.py` exercises the real
  projector chain end to end, including the fail-closed cases.
