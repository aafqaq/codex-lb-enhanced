"""Runtime trace-channel resolution.

Verbose logging is an incident tool that writes user prompts and model output to
the container log, so the rules that decide whether it is on are worth pinning
down: an upgrade must not change what an env-configured deployment emits, and
the dashboard toggle must be the whole answer once an operator has used it.
"""

from __future__ import annotations

import pytest

from app.core.config import trace as trace_module
from app.core.config.trace import (
    DIAGNOSTIC_TRACE_CHANNELS,
    PAYLOAD_TRACE_CHANNELS,
    effective_trace_channels,
    effective_verbose_logging,
    refresh_runtime_trace_channels,
    runtime_trace_channels_for,
    set_runtime_trace_channels,
)


@pytest.fixture(autouse=True)
def _clear_override():
    set_runtime_trace_channels(None)
    yield
    set_runtime_trace_channels(None)


class _EnvSettings:
    def __init__(self, trace: str) -> None:
        self.trace_channels = frozenset(entry.strip().lower() for entry in trace.split(",") if entry.strip())


def _patch_env(monkeypatch: pytest.MonkeyPatch, trace: str) -> None:
    monkeypatch.setattr(trace_module, "get_settings", lambda: _EnvSettings(trace))


def test_env_drives_channels_until_an_operator_decides(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_env(monkeypatch, "shape,payload")
    assert effective_trace_channels() == frozenset({"shape", "payload"})


def test_override_is_the_whole_answer(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_env(monkeypatch, "shape,payload,upstream_events")
    refresh_runtime_trace_channels(True, False)
    channels = effective_trace_channels()
    assert channels == DIAGNOSTIC_TRACE_CHANNELS
    # The env asked for payloads; the operator did not. The operator wins, so a
    # dashboard switch labelled "no request bodies" actually stops writing them.
    assert not (channels & PAYLOAD_TRACE_CHANNELS)


def test_override_off_silences_env_channels(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_env(monkeypatch, "shape,payload,upstream_payload")
    refresh_runtime_trace_channels(False, False)
    assert effective_trace_channels() == frozenset()


def test_override_with_payloads_enables_both_groups(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_env(monkeypatch, "")
    refresh_runtime_trace_channels(True, True)
    assert effective_trace_channels() == DIAGNOSTIC_TRACE_CHANNELS | PAYLOAD_TRACE_CHANNELS


def test_null_override_restores_env(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_env(monkeypatch, "shape")
    refresh_runtime_trace_channels(True, True)
    assert effective_trace_channels() != frozenset({"shape"})
    refresh_runtime_trace_channels(None, None)
    assert effective_trace_channels() == frozenset({"shape"})


def test_reported_state_reflects_env_while_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_env(monkeypatch, "shape,upstream_summary")
    # The dashboard must not claim verbose logging is off while the env has it on.
    assert effective_verbose_logging(None, None) == (True, False)

    _patch_env(monkeypatch, "payload")
    assert effective_verbose_logging(None, None) == (True, True)

    _patch_env(monkeypatch, "")
    assert effective_verbose_logging(None, None) == (False, False)


def test_reported_state_uses_the_override_once_set(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_env(monkeypatch, "shape,payload")
    assert effective_verbose_logging(False, None) == (False, False)
    assert effective_verbose_logging(True, None) == (True, False)
    assert effective_verbose_logging(True, True) == (True, True)


def test_payload_channels_are_never_implied_by_diagnostics() -> None:
    assert not (DIAGNOSTIC_TRACE_CHANNELS & PAYLOAD_TRACE_CHANNELS)
    assert runtime_trace_channels_for(verbose=True, include_payloads=False) == DIAGNOSTIC_TRACE_CHANNELS
    assert runtime_trace_channels_for(verbose=False, include_payloads=True) == frozenset()
