<div align="center">

# Codex LB Enhanced

### A resilient Codex-compatible account-pool gateway

<p>
  <a href="https://github.com/aafqaq/codex-lb-enhanced/actions/workflows/build-custom-image.yml"><img src="https://github.com/aafqaq/codex-lb-enhanced/actions/workflows/build-custom-image.yml/badge.svg?branch=custom%2Fresilient-streams-v1.24" alt="Build"></a>
  <a href="https://github.com/aafqaq/codex-lb-enhanced/releases"><img src="https://img.shields.io/github/v/release/aafqaq/codex-lb-enhanced?display_name=tag&sort=semver" alt="Release"></a>
  <a href="https://github.com/aafqaq/codex-lb-enhanced/blob/main/LICENSE"><img src="https://img.shields.io/github/license/aafqaq/codex-lb-enhanced" alt="License"></a>
  <a href="https://github.com/aafqaq/codex-lb-enhanced/pkgs/container/codex-lb-enhanced"><img src="https://img.shields.io/badge/GHCR-ready-9b87f5?logo=docker&logoColor=white" alt="GHCR"></a>
</p>

<p><a href="./README.zh-CN.md">简体中文</a> · <a href="https://aafqaq.github.io/codex-lb-enhanced/">Documentation</a> · <a href="https://github.com/aafqaq/codex-lb-enhanced/issues">Issues</a> · <a href="https://github.com/aafqaq/codex-lb-enhanced/discussions">Discussions</a></p>

![Codex LB Enhanced](docs/screenshots/banner.jpg)

<p><em>Keep the pool. Keep the conversation. Recover the turn.</em></p>

</div>

> **Independent distribution.** Codex LB Enhanced is an independently maintained downstream of [Soju06/codex-lb](https://github.com/Soju06/codex-lb). It is not an official OpenAI or upstream Codex release. The upstream MIT license and copyright notices are retained.

## What it is

Codex LB is a load balancer for ChatGPT accounts. Pool multiple accounts, track usage, manage API keys, and view everything in a dashboard. It exposes OpenAI-compatible endpoints for Codex CLI, Codex IDE integrations, OpenCode, OpenClaw, Hermes Agent, and other OpenAI clients.

Codex LB Enhanced keeps that general-purpose foundation and concentrates on the failure modes that are most disruptive for long-running Codex conversations: an upstream WebSocket disappearing mid-turn, an account reaching its allowance, a delayed retry after the desktop has been closed, or a response arriving while bridge bookkeeping is still in progress.

## Why use Enhanced?

| | Upstream Codex LB | Codex LB Enhanced |
|---|---|---|
| Account pooling | Load balance across ChatGPT accounts | Same selector and scheduling semantics, plus request-scoped failover exclusions |
| Codex allowance | Pool-level upstream estimate | API-key limits are presented as native `x-codex-*` headers; no custom key falls back to the pool estimate |
| Quota exhaustion | A single exhausted account can terminate a turn | Walk eligible accounts before exposing a pool-wide limit; preserve the original 429 metadata |
| Interrupted WebSocket | Recovery depends on the active bridge/cache path | Pre-event transport failures can fall back to HTTP; delayed owner lookup uses durable request records |
| Mid-stream quota | Normal terminal error semantics | Never replay visible text/tool calls inside the proxy; hand the retry boundary back to the native Codex client |
| HTTP bridge | Sensitive to nested recovery and event/idle races | Fenced nested recovery, iterator cleanup, and receive-before-persist activity tracking |
| Compaction | A malformed 2xx envelope may look successful | Missing compaction output is treated as a retryable upstream protocol failure |
| Operations | Upstream image/release links | Independent GHCR image, release checks, and CI build workflow |

The enhanced behavior is layered on top of the original load balancer. It does **not** replace API-key enforcement, account assignment, reservations, routing strategies, or the ordinary `/v1` contract.

## Highlights

<table>
<tr><td><b>Account Pooling</b><br>Load balance across multiple ChatGPT accounts</td><td><b>Usage Tracking</b><br>Per-account tokens, cost, and historical trends</td><td><b>API Keys</b><br>Per-key token, cost, window, and model limits</td></tr>
<tr><td><b>Dashboard Auth</b><br>Password plus optional TOTP</td><td><b>OpenAI-compatible</b><br>Codex CLI, OpenCode, and other clients</td><td><b>Auto Model Sync</b><br>Available models fetched from upstream</td></tr>
<tr><td><b>Native Codex Quota</b><br>Primary, secondary, monthly, and credits headers</td><td><b>Continuity Recovery</b><br>Reconnect after transport loss or delayed retry</td><td><b>Transport Resilience</b><br>Safe WebSocket-to-HTTP fallback in auto mode</td></tr>
</table>

| Dashboard | Accounts |
|:---:|:---:|
| ![Dashboard](docs/screenshots/dashboard.jpg) | ![Accounts](docs/screenshots/accounts.jpg) |

## Quick start

```bash
docker volume create codex-lb-enhanced-data
docker run -d --name codex-lb-enhanced \
  --restart unless-stopped \
  -e CODEX_LB_HTTP_RESPONSES_SESSION_BRIDGE_AMBIGUOUS_CONTINUATION_RECOVERY_MODE=server_indefinite_recovery \
  -p 2455:2455 -p 1455:1455 \
  -v codex-lb-enhanced-data:/var/lib/codex-lb \
  ghcr.io/aafqaq/codex-lb-enhanced:latest
```

Open [localhost:2455](http://localhost:2455), add your accounts, create an API key, and configure your client for the Responses endpoint.

## Codex client setup

For Codex CLI or an IDE integration, configure `~/.codex/config.toml`:

```toml
model = "gpt-5.6-sol"
model_reasoning_effort = "xhigh"
model_provider = "codex-lb-enhanced"

[model_providers.codex-lb-enhanced]
name = "openai"
base_url = "http://127.0.0.1:2455/backend-api/codex"
wire_api = "responses"
supports_websockets = true
requires_openai_auth = true
```

| Client | Endpoint | Notes |
|---|---|---|
| **Codex CLI / IDE** | `/backend-api/codex` | Native Responses and compact routes |
| **OpenCode** | `/v1` | OpenAI-compatible API |
| **OpenClaw** | `/v1` | OpenAI-compatible API |
| **Hermes Agent** | `/v1` | OpenAI-compatible API |
| **OpenAI SDKs** | `/v1` | Standard API client configuration |

Remote clients need an API key created in the dashboard.

## How Enhanced recovery works

```text
Codex request
     │
     ├─ normal account selector (unchanged)
     │
     ├─ upstream quota? ── yes ──► exclude this account ──► next eligible account
     │                                  │
     │                                  └─ none left ──► native 429 / reset metadata
     │
     ├─ WebSocket fails before first event? ──► retry equivalent HTTP stream
     │
     └─ visible output already sent? ──► do not duplicate it;
                                        let Codex perform its native whole-turn retry
```

Transport failure and account exhaustion are treated as different evidence. Recovery is bounded by the request deadline, durable operation fences, and the eligible account pool; “indefinite recovery” means persistent retry eligibility, not an unbounded resource loop.

## Configuration and data

Settings use the `CODEX_LB_` prefix or `.env.local`; start with [`.env.example`](.env.example). SQLite is the default database backend and PostgreSQL is available through `CODEX_LB_DATABASE_URL`.

| Environment | Data path |
|---|---|
| Local / `uvx` | `~/.codex-lb/` |
| Docker | `/var/lib/codex-lb/` |

Always mount `/var/lib/codex-lb` to a named volume. Back up the data directory before upgrading and keep the previous image tag for rollback.

## Documentation and development

The documentation covers getting started, client setup, configuration, authentication, API keys, routing, database operation, deployment, and troubleshooting. See the [documentation site](https://aafqaq.github.io/codex-lb-enhanced/) or [Issues](https://github.com/aafqaq/codex-lb-enhanced/issues).

```bash
uv sync
uv run pytest

cd frontend
bun install
bun run dev
```

The `custom/resilient-streams-v1.24` branch builds automatically through [GitHub Actions](.github/workflows/build-custom-image.yml) and publishes to `ghcr.io/aafqaq/codex-lb-enhanced`.

## Scope and attribution

This downstream keeps the upstream account pooling, dashboard, usage tracking, API-key management, client compatibility, and deployment model. Enhanced changes are maintained here and are not automatically merged into upstream.

If you need the original general-purpose distribution, use [Soju06/codex-lb](https://github.com/Soju06/codex-lb). If your priority is resilient Codex desktop sessions, native per-key quota presentation, and recoverable long-lived turns, use this distribution.

## License

MIT — see [LICENSE](LICENSE).
