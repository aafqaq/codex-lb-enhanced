## 1. Recovery classification

- [x] 1.1 Accept completed portable commentary as a retained recovery boundary when the fresh user/developer turn IDs match.
- [x] 1.2 Preserve all existing fail-closed tool, file, hosted-state, and malformed-shape guards.

## 2. Bridge failover

- [x] 2.1 Retain a validated unanchored full-history body when a proxy/session anchor trims the first attempt.
- [x] 2.2 Invalidate a rejected continuity anchor so a later full-history client retry is not re-anchored.
- [x] 2.3 Exclude exhausted accounts per request and continue through the configured load-balancer policy until the eligible pool is exhausted.
- [x] 2.4 Never splice a replacement generation after downstream-visible model output.

## 3. Client recovery contracts

- [x] 3.1 Preserve Codex-native retry semantics that cause a full local-history resend.
- [x] 3.2 Keep non-Codex outward errors protocol-compatible without changing internal failover behavior.

## 4. Verification

- [x] 4.1 Add replay-safety tests for interrupted commentary, turn matching, and unsafe tool/file history.
- [x] 4.2 Add a bridge regression proving full history is not re-anchored after a rejected proxy anchor.
- [x] 4.3 Add quota failover tests proving account exclusion and terminal pool exhaustion semantics.
- [x] 4.4 Run focused tests and formatting/type checks; OpenSpec CLI is unavailable in this local environment.

## 5. Hard-affinity owner recovery

- [x] 5.1 Bound selection recovery when a manually paused hard sticky owner returns `hard_affinity_saturated`.
- [x] 5.2 Reallocate safe first-turn or verified account-neutral replay requests without changing other routing policies.
- [x] 5.3 Fail closed with a logged client-recoverable owner-unavailable response when no safe replay exists.
- [x] 5.4 Add regression coverage for paused-owner reallocation and bounded continuation failure.
