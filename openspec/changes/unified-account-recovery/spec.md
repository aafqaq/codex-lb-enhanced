# Unified account recovery

## Requirements

- The proxy MUST treat a definitive upstream quota response as a failure of the selected account, not as a terminal failure of the request.
- After an account is excluded, the next selection MUST detach account-owned sticky, legacy, and seed affinity before walking the eligible pool.
- An excluded account MUST NOT be returned by a fallback selection, even when a prompt-cache or session affinity record still points to it.
- Continuations MUST preserve the complete client payload; recovery MUST NOT truncate the conversation to a fixed number of turns.
- The proxy MUST surface a terminal error only after the eligible account pool is exhausted or no account-neutral replay is safe.
- Recovery decisions MUST remain independent from the configured normal account rotation strategy; the recovery layer may only add failed accounts to the current request's exclusion set.
