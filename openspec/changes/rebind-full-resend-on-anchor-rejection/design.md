# Design

The upstream event reader classifies `previous_response_not_found` (including
the equivalent invalid-request message) as a pre-dispatch anchor rejection.
If the request has no response id, no response events, no downstream-visible
output, and its captured fresh request projects to an account-neutral full
resend, the reader:

1. removes the stale anchor and all hard selection keys from the retry state;
2. excludes the rejecting account without changing its health;
3. marks an existing durable operation failed so the same operation identity
   can be re-fenced for the replacement owner;
4. invokes the existing pre-created failover selector, which walks the pool
   and rebinds the durable sticky owner after a successful replacement.

If projection or replacement fails, the request remains a retryable 502
`upstream_unavailable`. Short, file-bound, non-portable, or already-visible
requests retain the existing continuity error behavior.

