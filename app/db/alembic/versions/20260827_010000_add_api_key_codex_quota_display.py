"""add per-api-key Codex quota display settings

Revision ID: 20260827_010000_add_api_key_codex_quota_display
Revises: 20260827_000000_remove_anonymous_telemetry
Create Date: 2026-08-27
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260827_010000_add_api_key_codex_quota_display"
down_revision = "20260827_000000_remove_anonymous_telemetry"
branch_labels = None
depends_on = None


def _columns() -> set[str]:
    bind = op.get_bind()
    if not sa.inspect(bind).has_table("api_keys"):
        return set()
    return {column["name"] for column in sa.inspect(bind).get_columns("api_keys")}


def upgrade() -> None:
    columns = _columns()
    if "codex_quota_mode" not in columns:
        op.add_column(
            "api_keys",
            sa.Column(
                "codex_quota_mode",
                sa.String(),
                nullable=False,
                server_default=sa.text("'api_key'"),
            ),
        )
    if "codex_quota_passthrough_enabled" not in columns:
        op.add_column(
            "api_keys",
            sa.Column(
                "codex_quota_passthrough_enabled",
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
            ),
        )


def downgrade() -> None:
    columns = _columns()
    if "codex_quota_passthrough_enabled" in columns:
        op.drop_column("api_keys", "codex_quota_passthrough_enabled")
    if "codex_quota_mode" in columns:
        op.drop_column("api_keys", "codex_quota_mode")
