## ADDED Requirements

### Requirement: Anonymous HTTP bridge transport loss is account-neutral

An HTTP bridge upstream transport termination that carries no peer close frame,
including a locally synthesized RFC 6455 code `1006`, MUST NOT write account
health. This rule applies both before and after application response events are
observed. Observed events make replay unsafe but do not change failure
provenance. A local send failure MUST follow the same account-neutral rule.

The bridge MUST retire the affected physical socket, finalize pending request
ownership exactly once, and preserve fail-closed semantics for an ambiguously
dispatched request. Structured upstream errors and peer-authored non-clean close
frames retain their existing account-health behavior.

#### Scenario: Frame-less disconnect after output does not penalize the account

- **GIVEN** an HTTP bridge request has received response events
- **WHEN** the upstream transport ends without a peer close frame
- **THEN** the request fails terminally without transparent replay
- **AND** the selected account receives no health penalty
- **AND** the physical bridge session is retired

#### Scenario: Peer policy close remains account evidence

- **WHEN** upstream sends a non-clean policy close frame
- **THEN** the existing account-health classifier remains authoritative

#### Scenario: Ambiguous send failure remains terminal

- **WHEN** sending `response.create` fails after dispatch may have occurred
- **THEN** the bridge does not replay the retained body on another account
- **AND** the failure does not mutate selected-account health

### Requirement: Repeated anonymous bridge failures isolate continuity, not accounts

When the existing eventless bridge-failure window reaches its threshold, the
proxy MUST attempt to clear the affected durable continuity under the current
session owner fence. It MUST NOT translate anonymous transport evidence into
account error counts. A failed fenced clear MUST remain fail-closed and MUST NOT
fall back to an account penalty.

#### Scenario: Poisoned proxy anchor does not drain the pool

- **GIVEN** one durable bridge session repeatedly ends eventlessly without a
  peer-authored application error
- **WHEN** the failure threshold is reached
- **THEN** the proxy attempts one owner-fenced continuity reset
- **AND** it does not call the account error recorder
- **AND** unrelated requests may continue selecting the account

#### Scenario: Settlement remains ahead of continuity isolation

- **GIVEN** a failed bridge request owns an API-key usage reservation
- **WHEN** repeated-failure continuity isolation is evaluated
- **THEN** reservation cleanup completes first
- **AND** a failed cleanup prevents the isolation signal from claiming success
