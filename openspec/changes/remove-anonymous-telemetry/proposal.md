# Remove anonymous telemetry

## Why

The enhanced build is intended for private, self-hosted deployments. Anonymous
install telemetry is not required for proxy operation and creates an outbound
data path, consent state, identity material, and dashboard surface that users
did not request.

## Scope

- Remove the anonymous telemetry scheduler, sender, snapshot builder, consent API,
  configuration, persisted identity fields, dashboard UI, mocks, and documentation.
- Remove the telemetry endpoint from the application routing and startup/shutdown
  lifecycle so no anonymous telemetry network request can be made.
- Keep local request logs, usage accounting, diagnostics, and OpenTelemetry
  tracing unchanged; those are operator-controlled functionality and are not the
  anonymous install telemetry being removed.
- Keep the historical Alembic migration in the repository for migration graph
  compatibility, then add a forward migration that removes the obsolete
  anonymous-telemetry columns from existing databases.

## Compatibility

This is a deliberate removal. Existing `CODEX_LB_TELEMETRY_ENABLED` and
`CODEX_LB_TELEMETRY_ENDPOINT` values become unused. The proxy, dashboard, usage
reports, and tracing continue to work normally.
