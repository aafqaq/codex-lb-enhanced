"""add dashboard verbose logging toggles

Revision ID: 20260830_000000_add_dashboard_verbose_logging
Revises: 20260827_010000_add_api_key_codex_quota_display
Create Date: 2026-08-30
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.engine import Connection

revision = "20260830_000000_add_dashboard_verbose_logging"
down_revision = "20260827_010000_add_api_key_codex_quota_display"
branch_labels = None
depends_on = None

_TABLE = "dashboard_settings"
# Nullable on purpose: NULL means "no operator decision recorded", which keeps
# CODEX_LB_TRACE authoritative so an upgrade cannot silently change what an
# existing env-configured deployment logs.
_COLUMNS = ("verbose_logging_enabled", "verbose_logging_include_payloads")


def _columns(connection: Connection, table_name: str) -> set[str]:
    inspector = sa.inspect(connection)
    if not inspector.has_table(table_name):
        return set()
    return {str(column["name"]) for column in inspector.get_columns(table_name) if column.get("name") is not None}


def upgrade() -> None:
    bind = op.get_bind()
    existing = _columns(bind, _TABLE)
    if not existing:
        return
    missing = [name for name in _COLUMNS if name not in existing]
    if not missing:
        return
    with op.batch_alter_table(_TABLE) as batch_op:
        for name in missing:
            batch_op.add_column(sa.Column(name, sa.Boolean(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    existing = _columns(bind, _TABLE)
    present = [name for name in _COLUMNS if name in existing]
    if not present:
        return
    with op.batch_alter_table(_TABLE) as batch_op:
        for name in present:
            batch_op.drop_column(name)
