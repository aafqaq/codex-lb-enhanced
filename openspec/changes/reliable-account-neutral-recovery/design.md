# Design

The request state keeps an immutable-at-the-request-lifecycle serialized
snapshot of the account-neutral full resend whenever the incoming request is
full-resend-shaped. The snapshot is captured before session/durable anchor
injection and before prefix trimming. The optimized request body remains
separate and may contain only the incremental suffix.

Recovery source selection follows this order:

1. verified full-resend snapshot;
2. a previously verified fresh replay body;
3. the current request body only when it is already unanchored.

For a definitive pre-dispatch quota response or rejected proxy-injected
anchor, the bridge strips `previous_response_id`, projects the snapshot through
the existing account-neutral replay validator, excludes only the failed
account, and re-enters the existing selector with its configured routing
strategy. If no portable snapshot exists, the existing fail-closed behavior is
preserved. No client-visible error is emitted for an internally recoverable
account failure.

