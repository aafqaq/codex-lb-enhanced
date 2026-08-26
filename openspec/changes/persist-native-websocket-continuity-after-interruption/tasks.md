# Tasks

- [x] Refresh the bounded response-owner cache for abnormal as well as normal
  terminal finalization.
- [x] Keep durable request-log lookup available after process/socket loss.
- [x] Add regression coverage for reconnecting with `previous_response_id`
  after an interrupted turn and a cold in-memory owner cache (durable request
  log lookup path).
- [x] Verify the existing full-context fallback when the upstream reports
  `previous_response_not_found`.
