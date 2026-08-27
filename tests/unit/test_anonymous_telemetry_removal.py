from __future__ import annotations

import sqlite3

import pytest

from app.db.migrate import run_upgrade


@pytest.mark.unit
def test_head_migration_removes_legacy_anonymous_telemetry_columns(tmp_path) -> None:
    db_path = tmp_path / "telemetry-removal.sqlite"
    db_url = f"sqlite:///{db_path}"

    run_upgrade(db_url, "20260806_000000_add_anonymous_telemetry", bootstrap_legacy=False)
    with sqlite3.connect(db_path) as connection:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(dashboard_settings)")}
    assert {"telemetry_consent", "telemetry_instance_id", "telemetry_private_key_encrypted"} <= columns

    run_upgrade(db_url, "head", bootstrap_legacy=False)
    with sqlite3.connect(db_path) as connection:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(dashboard_settings)")}
    assert not columns.intersection({"telemetry_consent", "telemetry_instance_id", "telemetry_private_key_encrypted"})
