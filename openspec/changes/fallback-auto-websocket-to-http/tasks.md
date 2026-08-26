# Tasks

- [x] Classify safe pre-event WebSocket transport failures in `auto` mode.
- [x] Retry the same request over HTTP with the HTTP-specific payload and
  headers.
- [x] Keep structured upstream errors and forced WebSocket behavior unchanged.
- [x] Prevent fallback after any downstream-visible event.
- [x] Add regression tests for handshake rejection, connect timeout, and a
  close before the first event.
- [x] Verify deferred circuit-breaker accounting across WebSocket failure and
  successful HTTP completion.
- [ ] Run the complete affected proxy test suites and static checks.
