## ADDED Requirements

### Requirement: The API key editor exposes Codex Fast mode as a switch

The API key edit dialog MUST offer a Force Fast mode switch. The switch MUST
read as enabled exactly when the key's enforced service tier is Codex's Fast
tier, which is sent upstream as `priority`. Enabling it MUST set that tier.
Disabling it MUST clear the enforced tier only when the current value is the
Fast tier, so that a key pinned to another tier is not silently reset. The
enforced service tier dropdown MUST continue to offer every tier it already
supported.

#### Scenario: Operator forces Fast mode on a key

- **GIVEN** an API key with no enforced service tier
- **WHEN** the operator enables Force Fast mode and saves
- **THEN** the update request carries the Fast tier as `priority`

#### Scenario: Operator turns Fast mode back off

- **GIVEN** an API key whose enforced service tier is the Fast tier
- **WHEN** the operator disables Force Fast mode and saves
- **THEN** the update request clears the enforced service tier

#### Scenario: A non-Fast tier survives an unrelated edit

- **GIVEN** an API key whose enforced service tier is `flex`
- **THEN** the Force Fast mode switch reads as disabled
- **AND** saving without touching it preserves `flex`
