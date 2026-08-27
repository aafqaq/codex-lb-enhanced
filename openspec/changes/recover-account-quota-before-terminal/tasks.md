## 1. Structured quota cause

- [x] 1.1 Preserve `usage_limit_reached` from the account selector for all proxy
      request kinds and log the preferred owner/reset hint.
- [x] 1.2 Add regression coverage for selection-time quota on HTTP/SSE and WebSocket
      continuations.

## 2. Safe account movement

- [x] 2.1 Move a verified full-resend continuation away from a quota-exhausted
      HTTP-bridge owner.
- [x] 2.2 Move a verified full-resend direct WebSocket continuation away from a
      quota-exhausted owner and synchronize the replay body at the send boundary.
- [x] 2.3 Permit repeated created-only quota terminals to walk the finite pool while
      retaining fail-closed behavior for visible output, files, and opaque deltas.

## 3. Verification

- [x] 3.1 Run focused unit and integration quota/replay tests.
- [x] 3.2 Run compile, diff, and Ruff checks.
- [ ] 3.3 Run strict OpenSpec validation in the release environment.
