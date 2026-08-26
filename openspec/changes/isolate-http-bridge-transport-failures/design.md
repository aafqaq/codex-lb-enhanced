# Design

## Failure provenance

The bridge distinguishes three failure sources:

1. A structured upstream application error or peer-authored policy close is
   account evidence and keeps the existing health behavior.
2. A frame-less close (`None` or synthetic RFC 6455 code `1006`) is transport
   evidence. It retires the physical socket and fails ambiguous work, but does
   not mutate account health.
3. A local send failure is transport evidence. Delivery may be ambiguous, so it
   is terminal and account-neutral rather than replayed.

The number of response events does not change transport provenance. Events make
replay unsafe, but they do not prove that the selected account caused the TCP or
WebSocket loss.

## Repeated failures

Three eventless anonymous transport failures inside the existing five-minute
window trigger an owner-fenced durable continuity reset instead of
`record_errors(account, 2)`. This targets a poisoned proxy-injected anchor and
prevents the same continuity failure from walking across the pool. If the row
cannot be cleared under its owner fence, the bridge still retires the socket and
fails closed; it does not compensate by penalizing the account.

## Safety invariants

- Ambiguous post-dispatch work is never transparently moved to another account.
- API-key reservations and request logs settle before any later health action.
- Explicit upstream errors continue through the current health classifier.
- Session retirement and retry-circuit behavior remain bounded.
