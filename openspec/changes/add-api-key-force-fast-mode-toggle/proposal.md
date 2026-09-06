# Change: Surface a Force Fast mode toggle on an API key

## Why

Codex calls its accelerated tier "Fast" and sends it upstream as
`service_tier: "priority"` (`ServiceTier::Fast.request_value()` in the Codex
protocol crate, which accepts `fast` and `priority` interchangeably). An API
key can already pin that tier through `enforced_service_tier`, but the
dashboard only exposes it as one option inside a five-value "Enforced service
tier" dropdown, where `priority` reads as an unrelated scheduling knob rather
than "always use Fast".

## What Changes

- Add a Force Fast mode switch to the API key edit dialog. Enabling it sets
  the key's enforced service tier to Codex's Fast tier; disabling it clears
  only that enforcement and leaves any other configured tier untouched.
- No backend, schema, or upstream contract change: the switch writes the
  existing `enforcedServiceTier` field.

## Impact

- Affected surface: the dashboard API key edit dialog and its locale strings.
- The existing enforced service tier dropdown keeps every value it had,
  including `flex` and `ultrafast`.
