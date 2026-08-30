"""Effective trace-channel resolution.

Trace logging is an incident tool: the payload channels carry user prompts and
model output, and the per-frame channels emit one record per upstream event, so
a long session can produce hundreds of megabytes. It therefore has to be
switchable while the process is running, not only through ``CODEX_LB_TRACE`` at
container start.

Precedence is deliberately simple so the dashboard toggle does exactly what it
says: once an operator has set the runtime override, it is the whole answer.
``CODEX_LB_TRACE`` applies only while the override is unset, which keeps
existing env-configured deployments behaving exactly as before an upgrade.

The getter is synchronous and allocation-free because it runs on per-request and
per-frame paths. The override is a plain module global refreshed by
``SettingsCache`` whenever it loads the dashboard row.
"""

from __future__ import annotations

from app.core.config.settings import get_settings

# Channels that describe routing and transport decisions without reproducing
# conversation content. Safe to leave on while reproducing an incident.
DIAGNOSTIC_TRACE_CHANNELS = frozenset(
    {
        "shape",
        "service_tier",
        "upstream_summary",
        "upstream_events",
        "client_events",
    }
)
# Channels that reproduce request/response bodies -- user prompts, model output,
# and the raw prompt cache key. Separated so verbose diagnostics do not force an
# operator to also write conversation content to the container log.
PAYLOAD_TRACE_CHANNELS = frozenset(
    {
        "payload",
        "upstream_payload",
        "upstream_event_payload",
        "client_event_payload",
        "shape_raw_cache_key",
    }
)

_runtime_trace_channels: frozenset[str] | None = None


def runtime_trace_channels_for(*, verbose: bool, include_payloads: bool) -> frozenset[str]:
    """Map the two dashboard toggles onto concrete channel names."""

    if not verbose:
        return frozenset()
    if include_payloads:
        return DIAGNOSTIC_TRACE_CHANNELS | PAYLOAD_TRACE_CHANNELS
    return DIAGNOSTIC_TRACE_CHANNELS


def set_runtime_trace_channels(channels: frozenset[str] | None) -> None:
    """Install (or clear, with ``None``) the runtime override."""

    global _runtime_trace_channels
    _runtime_trace_channels = channels


def get_runtime_trace_channels() -> frozenset[str] | None:
    return _runtime_trace_channels


def effective_trace_channels(env_channels: frozenset[str] | None = None) -> frozenset[str]:
    """Channels this process should emit right now.

    Callers pass their own ``Settings.trace_channels`` so the env fallback stays
    a visible dependency of the calling module rather than a hidden global read.
    """

    override = _runtime_trace_channels
    if override is not None:
        return override
    if env_channels is not None:
        return env_channels
    return get_settings().trace_channels


def effective_verbose_logging(
    verbose_logging_enabled: bool | None,
    verbose_logging_include_payloads: bool | None,
) -> tuple[bool, bool]:
    """Resolve the stored override into the state the dashboard should show.

    While no operator decision is recorded (both columns NULL) the answer is
    derived from ``CODEX_LB_TRACE`` so the dashboard reports what the process is
    actually emitting rather than a default that contradicts it.
    """

    if verbose_logging_enabled is None:
        env_channels = get_settings().trace_channels
        return (
            bool(env_channels & DIAGNOSTIC_TRACE_CHANNELS) or bool(env_channels & PAYLOAD_TRACE_CHANNELS),
            bool(env_channels & PAYLOAD_TRACE_CHANNELS),
        )
    return verbose_logging_enabled, bool(verbose_logging_include_payloads)


def refresh_runtime_trace_channels(
    verbose_logging_enabled: bool | None,
    verbose_logging_include_payloads: bool | None,
) -> None:
    """Install the override implied by a freshly loaded dashboard row."""

    if verbose_logging_enabled is None:
        set_runtime_trace_channels(None)
        return
    set_runtime_trace_channels(
        runtime_trace_channels_for(
            verbose=verbose_logging_enabled,
            include_payloads=bool(verbose_logging_include_payloads),
        )
    )
