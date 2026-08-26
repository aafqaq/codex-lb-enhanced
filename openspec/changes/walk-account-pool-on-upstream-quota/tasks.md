# Tasks

- [x] Normalize structured and message-only account quota failures.
- [x] Walk all eligible accounts before visible output and bound retries by the
  per-request exclusion set.
- [x] Surface pool-wide `usage_limit_reached` only after selection is exhausted.
- [x] Add a private Codex native-client retry boundary for failures after visible
  output.
- [x] Preserve explicit terminal guarding on the public `/v1` contract.
- [x] Add regression coverage for raw SSE, native WebSocket, HTTP bridge, pool
  exhaustion, and post-output retry behavior.
- [ ] Run the complete affected proxy test suites and static checks.
