# Tasks

- [x] Remove backend telemetry module, lifecycle wiring, router, settings, and ORM fields.
- [x] Add the forward database migration for obsolete telemetry columns.
- [x] Remove telemetry-specific backend tests and fixtures.
- [x] Remove dashboard telemetry components, hooks, schemas, mocks, locales, and smoke/integration coverage.
- [x] Remove telemetry documentation and settings-reference entries.
- [x] Verify no runtime anonymous telemetry references remain and run backend checks; frontend typecheck is unavailable because bun/node dependencies are not installed in this workspace.
