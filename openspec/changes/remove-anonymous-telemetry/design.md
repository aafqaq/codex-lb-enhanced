# Design

Anonymous telemetry is removed at every layer rather than merely disabled by a
default. There is no scheduler instance, HTTP client, telemetry router, consent
store, signing identity, or telemetry-specific settings field after this change.

The old migration that introduced telemetry remains immutable so databases that
already ran it can still traverse the Alembic history. A new head migration
conditionally drops the three obsolete `dashboard_settings` columns using the
same safe batch-operation pattern used by the existing migrations. Downgrading
the removal migration restores the columns with their original defaults.

The term “telemetry” used by usage-history durability comments and OpenTelemetry
tracing is intentionally out of scope: neither sends the anonymous install
snapshot and both remain required by existing operator features.
