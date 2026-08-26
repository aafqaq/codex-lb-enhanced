## ADDED Requirements

### Requirement: API-key custom limits are presented as native Codex allowance

For a request authenticated by a Codex LB API key, the proxy MUST inspect that
key's active global custom limits.  If at least one supported global limit is
configured, response metadata and `/api/codex/usage` MUST describe the key's
own budget instead of the upstream account pool.

The mapping MUST use `5h` before `daily` for the primary window, `7d` before
`weekly` for the secondary window, and `monthly` for the monthly window.  When
multiple limit types share a window, selection priority MUST be credits, total
tokens, cost, input tokens, then output tokens.  Model-filtered limits MUST NOT
be presented as a global client allowance.

#### Scenario: Token and cost budgets become Codex windows

- **GIVEN** an API key has used 250 of 1000 daily total tokens
- **AND** it has used 1200 of 10000 weekly cost units
- **WHEN** the key calls a Codex Responses route
- **THEN** primary used percent is 25
- **AND** secondary used percent is 12
- **AND** pooled-account percentages are not returned

#### Scenario: Current reservation does not inflate the display

- **GIVEN** request admission temporarily reserves the remaining API-key budget
- **WHEN** response headers are generated before actual usage is settled
- **THEN** the reservation for that request is subtracted from displayed usage
- **AND** the client does not see 100 percent solely because the request began

### Requirement: Keys without custom limits retain pooled quota estimates

When an authenticated API key has no supported global custom limit, the proxy
MUST retain the existing pooled-account quota response unless the administrator
has enabled the existing hide-upstream-quota policy.  The hide policy MUST
continue to suppress pooled quota metadata in that fallback case.

#### Scenario: Unlimited key uses pool estimate

- **GIVEN** an API key has no custom limit
- **AND** pooled quota hiding is disabled
- **WHEN** the key calls a Codex route
- **THEN** the response contains the existing account-pool estimate

#### Scenario: Pool estimate is hidden by policy

- **GIVEN** an API key has no custom limit
- **AND** pooled quota hiding is enabled
- **THEN** no pooled Codex quota headers are emitted
