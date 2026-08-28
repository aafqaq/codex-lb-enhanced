# Tasks

- [x] Reuse the request-lifecycle full-resend snapshot separate from the trimmed
  upstream body.
- [x] Centralize portable recovery source selection for anchor and quota
  failures.
- [x] Ensure each failed account is excluded while the configured selector
  strategy remains authoritative for the next account.
- [x] Add regression coverage for 568-item-to-3-item optimization followed by
  quota failover, anchor rejection, and multi-account A→B→C traversal.
- [x] Run bridge tests and static checks; OpenSpec validation is pending in CI.
