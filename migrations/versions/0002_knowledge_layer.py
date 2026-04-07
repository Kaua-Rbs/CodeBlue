"""Add knowledge layer tables and rule provenance fields."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0002_knowledge_layer"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "risk_assessments",
        sa.Column("knowledge_bundle_id", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "risk_assessments",
        sa.Column("triggering_rule_ids", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "risk_assessments",
        sa.Column("context_facts", sa.JSON(), nullable=False, server_default="{}"),
    )
    op.create_index(
        "ix_risk_assessments_knowledge_bundle_id",
        "risk_assessments",
        ["knowledge_bundle_id"],
    )

    op.add_column(
        "proposed_actions",
        sa.Column("action_definition_id", sa.String(length=64), nullable=True),
    )
    op.add_column("proposed_actions", sa.Column("category", sa.String(length=64), nullable=True))
    op.add_column(
        "proposed_actions",
        sa.Column("execution_mode", sa.String(length=32), nullable=False, server_default="review_only"),
    )
    op.add_column(
        "proposed_actions",
        sa.Column("knowledge_bundle_id", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "proposed_actions",
        sa.Column("triggering_rule_ids", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.create_index(
        "ix_proposed_actions_knowledge_bundle_id",
        "proposed_actions",
        ["knowledge_bundle_id"],
    )

    op.create_table(
        "knowledge_bundles",
        sa.Column("bundle_id", sa.String(length=64), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("version", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("jurisdiction", sa.String(length=64), nullable=False),
        sa.Column("organization", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
    )

    op.create_table(
        "knowledge_source_documents",
        sa.Column("source_document_id", sa.String(length=64), primary_key=True),
        sa.Column("bundle_id", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("organization", sa.String(length=255), nullable=False),
        sa.Column("document_type", sa.String(length=64), nullable=False),
        sa.Column("publication_date", sa.String(length=32), nullable=True),
        sa.Column("version_label", sa.String(length=64), nullable=True),
        sa.Column("jurisdiction", sa.String(length=64), nullable=False),
        sa.Column("setting_scope", sa.JSON(), nullable=False),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("language", sa.String(length=16), nullable=False),
        sa.Column("machine_readability", sa.String(length=32), nullable=False),
        sa.Column("ingestion_mode", sa.String(length=32), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["bundle_id"], ["knowledge_bundles.bundle_id"]),
    )

    op.create_table(
        "knowledge_pathogen_packs",
        sa.Column("pathogen_pack_id", sa.String(length=64), primary_key=True),
        sa.Column("bundle_id", sa.String(length=64), nullable=False),
        sa.Column("pathogen_code", sa.String(length=64), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("version", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("source_document_ids", sa.JSON(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["bundle_id"], ["knowledge_bundles.bundle_id"]),
    )

    op.create_table(
        "knowledge_policy_packs",
        sa.Column("policy_pack_id", sa.String(length=64), primary_key=True),
        sa.Column("bundle_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("version", sa.String(length=32), nullable=False),
        sa.Column("jurisdiction", sa.String(length=64), nullable=False),
        sa.Column("organization", sa.String(length=255), nullable=False),
        sa.Column("source_document_ids", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["bundle_id"], ["knowledge_bundles.bundle_id"]),
    )

    op.create_table(
        "knowledge_review_workflow_packs",
        sa.Column("workflow_pack_id", sa.String(length=64), primary_key=True),
        sa.Column("bundle_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("version", sa.String(length=32), nullable=False),
        sa.Column("source_document_ids", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["bundle_id"], ["knowledge_bundles.bundle_id"]),
    )

    op.create_table(
        "knowledge_action_definitions",
        sa.Column("action_id", sa.String(length=64), primary_key=True),
        sa.Column("bundle_id", sa.String(length=64), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("subtype", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("pathogen_specificity", sa.JSON(), nullable=False),
        sa.Column("execution_mode", sa.String(length=32), nullable=False),
        sa.Column("requires_reviewer_role", sa.String(length=64), nullable=False),
        sa.Column("target_scope", sa.String(length=32), nullable=False),
        sa.Column("must_be_logged", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["bundle_id"], ["knowledge_bundles.bundle_id"]),
    )

    op.create_table(
        "knowledge_evidence_statements",
        sa.Column("evidence_statement_id", sa.String(length=64), primary_key=True),
        sa.Column("bundle_id", sa.String(length=64), nullable=False),
        sa.Column("statement", sa.Text(), nullable=False),
        sa.Column("evidence_type", sa.String(length=64), nullable=False),
        sa.Column("source_document_ids", sa.JSON(), nullable=False),
        sa.Column("confidence", sa.String(length=32), nullable=False),
        sa.Column("uncertainty_note", sa.Text(), nullable=True),
        sa.Column("applies_to", sa.JSON(), nullable=False),
        sa.Column("used_by_rule_ids", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["bundle_id"], ["knowledge_bundles.bundle_id"]),
    )

    op.create_table(
        "knowledge_terminology_bindings",
        sa.Column("binding_id", sa.String(length=64), primary_key=True),
        sa.Column("bundle_id", sa.String(length=64), nullable=False),
        sa.Column("local_system", sa.String(length=64), nullable=False),
        sa.Column("local_code", sa.String(length=64), nullable=False),
        sa.Column("local_display", sa.String(length=255), nullable=False),
        sa.Column("canonical_field", sa.String(length=128), nullable=False),
        sa.Column("canonical_value", sa.String(length=128), nullable=False),
        sa.ForeignKeyConstraint(["bundle_id"], ["knowledge_bundles.bundle_id"]),
    )

    op.create_table(
        "knowledge_rule_artifacts",
        sa.Column("rule_id", sa.String(length=64), primary_key=True),
        sa.Column("bundle_id", sa.String(length=64), nullable=False),
        sa.Column("rule_kind", sa.String(length=64), nullable=False),
        sa.Column("owner_pack_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("condition_payload", sa.JSON(), nullable=False),
        sa.Column("outputs_payload", sa.JSON(), nullable=False),
        sa.Column("source_document_ids", sa.JSON(), nullable=False),
        sa.Column("confidence", sa.String(length=32), nullable=True),
        sa.Column("uncertainty_note", sa.Text(), nullable=True),
        sa.Column("version", sa.String(length=32), nullable=False),
        sa.ForeignKeyConstraint(["bundle_id"], ["knowledge_bundles.bundle_id"]),
    )
    op.create_index(
        "ix_knowledge_rule_artifacts_owner_pack_id",
        "knowledge_rule_artifacts",
        ["owner_pack_id"],
    )
    op.create_index(
        "ix_knowledge_rule_artifacts_rule_kind",
        "knowledge_rule_artifacts",
        ["rule_kind"],
    )

    op.create_table(
        "knowledge_test_cases",
        sa.Column("test_case_id", sa.String(length=64), primary_key=True),
        sa.Column("bundle_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("input_facts", sa.JSON(), nullable=False),
        sa.Column("expected_outputs", sa.JSON(), nullable=False),
        sa.Column("unexpected_outputs", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["bundle_id"], ["knowledge_bundles.bundle_id"]),
    )


def downgrade() -> None:
    op.drop_table("knowledge_test_cases")
    op.drop_index("ix_knowledge_rule_artifacts_rule_kind", table_name="knowledge_rule_artifacts")
    op.drop_index(
        "ix_knowledge_rule_artifacts_owner_pack_id",
        table_name="knowledge_rule_artifacts",
    )
    op.drop_table("knowledge_rule_artifacts")
    op.drop_table("knowledge_terminology_bindings")
    op.drop_table("knowledge_evidence_statements")
    op.drop_table("knowledge_action_definitions")
    op.drop_table("knowledge_review_workflow_packs")
    op.drop_table("knowledge_policy_packs")
    op.drop_table("knowledge_pathogen_packs")
    op.drop_table("knowledge_source_documents")
    op.drop_table("knowledge_bundles")

    op.drop_index("ix_proposed_actions_knowledge_bundle_id", table_name="proposed_actions")
    op.drop_column("proposed_actions", "triggering_rule_ids")
    op.drop_column("proposed_actions", "knowledge_bundle_id")
    op.drop_column("proposed_actions", "execution_mode")
    op.drop_column("proposed_actions", "category")
    op.drop_column("proposed_actions", "action_definition_id")

    op.drop_index("ix_risk_assessments_knowledge_bundle_id", table_name="risk_assessments")
    op.drop_column("risk_assessments", "context_facts")
    op.drop_column("risk_assessments", "triggering_rule_ids")
    op.drop_column("risk_assessments", "knowledge_bundle_id")
