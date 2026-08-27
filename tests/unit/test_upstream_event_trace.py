from __future__ import annotations

import logging
from types import SimpleNamespace

import pytest

import app.core.clients.proxy as proxy_module

pytestmark = pytest.mark.unit


def test_upstream_event_trace_is_disabled_without_channel(monkeypatch, caplog):
    monkeypatch.setattr(
        proxy_module,
        "get_settings",
        lambda: SimpleNamespace(trace_channels=frozenset()),
    )

    with caplog.at_level(logging.INFO, logger="app.core.clients.proxy"):
        proxy_module._maybe_log_upstream_event(
            kind="responses",
            account_id="account-secret",
            transport="http_bridge",
            event_type="response.completed",
            payload={"response_id": "resp-secret"},
        )

    assert "upstream_event" not in caplog.text


def test_upstream_event_trace_hashes_ids_and_bounds_raw_payload(monkeypatch, caplog):
    monkeypatch.setattr(
        proxy_module,
        "get_settings",
        lambda: SimpleNamespace(trace_channels=frozenset({"upstream_events", "upstream_event_payload"})),
    )
    raw_text = "x" * (proxy_module._UPSTREAM_EVENT_PAYLOAD_MAX_CHARS + 1024)

    with caplog.at_level(logging.INFO, logger="app.core.clients.proxy"):
        proxy_module._maybe_log_upstream_event(
            kind="responses",
            account_id="account-secret",
            transport="websocket",
            event_type="error",
            payload={
                "response": {"id": "resp-secret"},
                "sequence_number": 7,
                "error": {"code": "usage_limit_reached", "message": "quota exhausted"},
            },
            raw_text=raw_text,
            response_events_seen=3,
        )

    assert "account-secret" not in caplog.text
    assert "resp-secret" not in caplog.text
    assert "account_id=sha256:" in caplog.text
    assert "response_id=sha256:" in caplog.text
    assert "error_code=usage_limit_reached" in caplog.text
    assert "response_events_seen=3" in caplog.text
    payload_records = [record for record in caplog.records if record.getMessage().startswith("upstream_event_payload")]
    assert len(payload_records) == 1
    assert len(payload_records[0].getMessage()) < proxy_module._UPSTREAM_EVENT_PAYLOAD_MAX_CHARS + 512


def test_client_websocket_trace_is_opt_in_and_bounded(monkeypatch, caplog):
    monkeypatch.setattr(
        proxy_module,
        "get_settings",
        lambda: SimpleNamespace(trace_channels=frozenset({"client_events", "client_event_payload"})),
    )
    raw_text = "y" * (proxy_module._UPSTREAM_EVENT_PAYLOAD_MAX_CHARS + 1024)

    with caplog.at_level(logging.INFO, logger="app.core.clients.proxy"):
        proxy_module._maybe_log_downstream_websocket_event(
            raw_text=raw_text,
            payload={"type": "response.create"},
        )

    assert "client_event request_id=" in caplog.text
    assert "event_type=response.create" in caplog.text
    payload_records = [record for record in caplog.records if record.getMessage().startswith("client_event_payload")]
    assert len(payload_records) == 1
    assert len(payload_records[0].getMessage()) < proxy_module._UPSTREAM_EVENT_PAYLOAD_MAX_CHARS + 512
