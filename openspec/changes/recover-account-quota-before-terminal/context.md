## Recovery model

The proxy must separate account selection from client presentation.  Every
transport receives the same structured selection cause.  Each transport then applies
the same safety rule: a request may move away from an owner only when its complete
input is locally verified as self-contained and account-neutral.  A file reference,
opaque delta, or visible model output remains bound to the current owner.

`response.created` is an acknowledgement, not model output.  If an upstream sends a
created frame and then reports `usage_limit_reached`, the bridge can retain the
public response id while replaying the request on another account.  Text, reasoning,
tool-call, or sequenced frames are never replayed automatically.

The exclusion set is per logical request.  It prevents A→B→A loops, permits the
normal routing strategy to choose B/C, and converts the final empty-selection result
back to the original pool-wide quota classification so clients receive the expected
official error semantics.

Selection-time quota and upstream quota use the same path.  This is important when
the background quota poll marks an account exhausted before the next continuation
arrives: the request must not first open a doomed socket merely to discover the same
429.
