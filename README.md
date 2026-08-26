# Codex LB Enhanced

An independently maintained Codex-compatible account-pool gateway. This project keeps the original codex-lb dashboard, API-key management, usage tracking, and account balancing while focusing on protocol fidelity and resilient conversations.

## Why this fork exists

Codex clients expect a long-lived, stateful upstream conversation. A transient websocket close, an exhausted account, a network interruption, or a delayed retry should not destroy that conversation. Codex LB Enhanced treats those events as transport and routing failures and recovers whenever another eligible account is available.

## Enhancements

- Account-pool failover on official usage-limit responses, including message-only limit errors.
- Native Codex retry boundaries so the official client can retry without losing the visible conversation or tool state.
- Durable response ownership after abnormal websocket termination, allowing a later retry or account switch to resume the same response.
- Automatic websocket-to-HTTP fallback for unstable upstream websocket connections.
- Codex-compatible quota headers. API-key-specific limits are exposed when configured; otherwise the response uses the pool estimate.
- Strict compaction-response validation and retry/failover for empty or malformed successful compaction responses.
- Long-lived conversation continuity across delayed retries, reconnects, account switches, and context compaction.
- Runtime update checks and published images point to this independent repository.

The quota headers mirror the fields understood by the Codex client (`x-codex-primary-*`, `x-codex-secondary-*`, and credits fields). They describe the limit assigned to the presented API key when one exists; they do not disclose upstream account credentials.

## Quick start

```bash
docker volume create codex-lb-enhanced-data
docker run -d --name codex-lb-enhanced \
  --restart unless-stopped \
  -p 1455:1455 -p 2455:2455 \
  -v codex-lb-enhanced-data:/var/lib/codex-lb \
  ghcr.io/aafqaq/codex-lb-enhanced:latest
```

Open `http://localhost:2455` for the dashboard. Configure the Codex client to use the gateway's Responses endpoint and an API key created in the dashboard.

## Development

The project is Python/FastAPI with a React frontend. Run the backend tests with:

```bash
uv run pytest
```

The `custom/resilient-streams-v1.24` branch is built automatically by GitHub Actions and published to GHCR as `ghcr.io/aafqaq/codex-lb-enhanced:latest` (plus an immutable commit tag).

## Data and upgrades

Keep `/var/lib/codex-lb` in a named volume. Upgrading the image does not replace that volume, so accounts, API keys, usage, and settings remain intact. Make a volume/database backup before upgrades and keep the previous image tag available for rollback.

## License

This repository retains the upstream MIT license and notices. It is an independent distribution maintained by `aafqaq`; it is not the upstream project's official release channel.
