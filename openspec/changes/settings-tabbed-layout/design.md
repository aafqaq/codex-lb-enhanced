# Design

The page owns a small local `SettingsTab` state. The initial tab is derived from
the existing settings deep links (`#firewall` opens Operations and the legacy
`?advanced=1` query opens Routing); clicking a tab updates
the URL hash for a stable bookmark without changing the route. Each tab panel uses
CSS grid classes (`lg:grid-cols-2`) and keeps the existing card components intact.

Advanced settings remain available, but are categorized instead of hidden behind
one collapsible group. Only the active panel is mounted, so expensive settings
queries retain the previous lazy behavior in practice.
