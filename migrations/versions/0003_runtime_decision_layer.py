"""Add direct action priority field."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0003_runtime_decision_layer"
down_revision = "0002_knowledge_layer"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "proposed_actions",
        sa.Column("priority", sa.String(length=16), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("proposed_actions", "priority")
