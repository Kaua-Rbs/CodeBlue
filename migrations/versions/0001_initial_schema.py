"""Initial CodeBlue schema."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "events",
        sa.Column("event_id", sa.String(length=36), primary_key=True),
        sa.Column("event_type", sa.String(length=64), nullable=False, index=True),
        sa.Column("hospital_id", sa.String(length=64), nullable=False, index=True),
        sa.Column("source_system", sa.String(length=128), nullable=False),
        sa.Column("schema_version", sa.String(length=32), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
    )

    op.create_table(
        "risk_assessments",
        sa.Column("assessment_id", sa.String(length=36), primary_key=True),
        sa.Column("entity_scope", sa.String(length=32), nullable=False),
        sa.Column("target_id", sa.String(length=128), nullable=False, index=True),
        sa.Column("time_window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("time_window_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("priority", sa.String(length=16), nullable=False),
        sa.Column("generated_by", sa.String(length=64), nullable=False),
        sa.Column("pathogen_pack_version", sa.String(length=32), nullable=False),
        sa.Column("policy_pack_version", sa.String(length=32), nullable=False),
        sa.Column("signals_payload", sa.JSON(), nullable=False),
    )

    op.create_table(
        "priority_alerts",
        sa.Column("alert_id", sa.String(length=36), primary_key=True),
        sa.Column("assessment_id", sa.String(length=36), nullable=False),
        sa.Column("target_id", sa.String(length=128), nullable=False, index=True),
        sa.Column("priority", sa.String(length=16), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("signals_payload", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["assessment_id"], ["risk_assessments.assessment_id"]),
    )

    op.create_table(
        "audit_records",
        sa.Column("audit_id", sa.String(length=36), primary_key=True),
        sa.Column("record_type", sa.String(length=64), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("actor", sa.String(length=128), nullable=False),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("entity_id", sa.String(length=128), nullable=False, index=True),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column("schema_version", sa.String(length=32), nullable=True),
        sa.Column("pathogen_pack_version", sa.String(length=32), nullable=True),
        sa.Column("policy_pack_version", sa.String(length=32), nullable=True),
        sa.Column("scoring_version", sa.String(length=32), nullable=True),
        sa.Column("source_event_ids", sa.JSON(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=True),
    )

    op.create_table(
        "proposed_actions",
        sa.Column("action_id", sa.String(length=36), primary_key=True),
        sa.Column("risk_assessment_id", sa.String(length=36), nullable=True),
        sa.Column("action_type", sa.String(length=64), nullable=False),
        sa.Column("target_scope", sa.String(length=32), nullable=False),
        sa.Column("target_id", sa.String(length=128), nullable=False, index=True),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("required_reviewer_role", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("constraints_applied", sa.JSON(), nullable=False),
        sa.Column("audit_ref", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["audit_ref"], ["audit_records.audit_id"]),
        sa.ForeignKeyConstraint(["risk_assessment_id"], ["risk_assessments.assessment_id"]),
    )

    op.create_table(
        "review_decisions",
        sa.Column("decision_id", sa.String(length=36), primary_key=True),
        sa.Column("action_id", sa.String(length=36), nullable=False),
        sa.Column("reviewer_role", sa.String(length=64), nullable=False),
        sa.Column("decision", sa.String(length=32), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("audit_ref", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["action_id"], ["proposed_actions.action_id"]),
        sa.ForeignKeyConstraint(["audit_ref"], ["audit_records.audit_id"]),
    )


def downgrade() -> None:
    op.drop_table("review_decisions")
    op.drop_table("proposed_actions")
    op.drop_table("audit_records")
    op.drop_table("priority_alerts")
    op.drop_table("risk_assessments")
    op.drop_table("events")
