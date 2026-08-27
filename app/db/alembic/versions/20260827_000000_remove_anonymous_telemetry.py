"""remove anonymous telemetry state

Revision ID: 20260827_000000_remove_anonymous_telemetry
Revises: 20260816_000000_add_model_source_embeddings
Create Date: 2026-08-27
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260827_000000_remove_anonymous_telemetry"
down_revision = "20260816_000000_add_model_source_embeddings"
branch_labels = None
depends_on = None

_TABLE = "dashboard_settings"
_COLUMNS = (
    "telemetry_private_key_encrypted",
    "telemetry_instance_id",
    "telemetry_consent",
)


def _column_names() -> set[str]:
    bind = op.get_bind()
    if not sa.inspect(bind).has_table(_TABLE):
        return set()
    return {column["name"] for column in sa.inspect(bind).get_columns(_TABLE)}


def upgrade() -> None:
    columns = _column_names()
    if not columns.intersection(_COLUMNS):
        return
    with op.batch_alter_table(_TABLE) as batch_op:
        for column_name in _COLUMNS:
            if column_name in columns:
                batch_op.drop_column(column_name)


def downgrade() -> None:
    columns = _column_names()
    with op.batch_alter_table(_TABLE) as batch_op:
        if "telemetry_consent" not in columns:
            batch_op.add_column(
                sa.Column(
                    "telemetry_consent",
                    sa.String(length=16),
                    nullable=False,
                    server_default=sa.text("'undecided'"),
                )
            )
        if "telemetry_instance_id" not in columns:
            batch_op.add_column(sa.Column("telemetry_instance_id", sa.String(length=36), nullable=True))
        if "telemetry_private_key_encrypted" not in columns:
            batch_op.add_column(sa.Column("telemetry_private_key_encrypted", sa.LargeBinary(), nullable=True))
