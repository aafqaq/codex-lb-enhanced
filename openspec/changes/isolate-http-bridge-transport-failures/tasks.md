# Tasks

- [x] Classify frame-less HTTP bridge disconnects as account-neutral regardless
  of response-event count.
- [x] Classify HTTP bridge send failures as account-neutral ambiguous transport
  failures.
- [x] Replace repeated eventless transport account penalties with owner-fenced
  continuity reset.
- [x] Add regression tests for mid-stream disconnects, repeated eventless
  failures, explicit peer close codes, and settlement ordering.
- [x] Run targeted HTTP bridge tests and static checks.
- [x] Build an isolated image and validate it without changing production ports,
  containers, volumes, or Nginx.
