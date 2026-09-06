## MODIFIED Requirements

### Requirement: Upstream quota exhaustion consumes the eligible account pool

When an upstream account reports an allowance exhaustion code, or reports the
equivalent usage-limit message without a stable code, the proxy MUST classify
the condition as selected-account quota evidence.  Before any model output is
visible, the proxy MUST exclude that account and attempt every other eligible
account allowed by request continuity and API-key assignment.  The ordinary
transient retry-count ceiling MUST NOT stop this finite pool walk.  The proxy
MUST expose `usage_limit_reached` only when no eligible replacement remains.

A request body that is not provably account-neutral records its dispatch owner
so a partially committed continuation cannot cross accounts.  A definitive
quota response proves the account accepted nothing, so for a request that
carries no account-owned anchor — no `previous_response_id` and no input-file
pin — the proxy MUST release that recorded owner and re-dispatch the client's
own transcript in its portable form.  The proxy MUST NOT ask account selection
for an account that the same walk has already excluded.

#### Scenario: Message-only quota switches accounts

- **GIVEN** the selected account returns `The usage limit has been reached`
  without a stable quota code
- **AND** no model output has been forwarded
- **WHEN** another assigned account is eligible
- **THEN** the failed account is marked exhausted and excluded
- **AND** the same request is dispatched on the replacement account
- **AND** no single-account quota event reaches the client

#### Scenario: A recorded dispatch owner does not block an unanchored turn

- **GIVEN** a first turn whose body carries client bookkeeping and response
  item ids, so the selected account was recorded as its dispatch owner
- **AND** that account returns usage-limit exhaustion before any output
- **WHEN** the pool walk selects a replacement account
- **THEN** the recorded owner is released and the transcript is re-dispatched
  without its response-owned item ids
- **AND** the client receives the replacement account's response instead of a
  `preferred_account_unavailable` selection failure

#### Scenario: Anchored continuations stay owner-bound

- **GIVEN** a continuation carrying `previous_response_id` or an input-file pin
- **WHEN** its owner reports usage-limit exhaustion
- **THEN** the recorded dispatch owner is retained
- **AND** the request does not silently move to another account

#### Scenario: Pool exhaustion is terminal

- **GIVEN** every eligible assigned account has returned quota exhaustion for
  the request
- **WHEN** account selection has no remaining candidate
- **THEN** the client receives `usage_limit_reached`
- **AND** the error is not disguised as a generic empty-pool failure
