# Rebind portable full resends after rejected anchors

When an HTTP bridge account rejects a `previous_response_id` before
`response.created`, a Codex request carrying a verified, portable full
transcript must be replayed on another eligible account immediately. The
current hard owner must be excluded for this operation, while short or
account-bound continuations remain fail-closed and preserve their existing
ownership semantics.

