## Requirement: Responsive settings and refresh
The settings page MUST keep cards within the viewport at narrow and wide breakpoints and MUST expose working retry/refresh actions for settings-owned data queries after stale-data or initial-load failures.

### Scenario: settings data retry
- WHEN a settings sub-query fails
- THEN its retry action invokes a fresh request and updates the rendered data when the request succeeds
