from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class EventRecord(Base):
    __tablename__ = "events"

    event_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    hospital_id: Mapped[str] = mapped_column(String(64), index=True)
    source_system: Mapped[str] = mapped_column(String(128))
    schema_version: Mapped[str] = mapped_column(String(32))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)


class RiskAssessmentRecord(Base):
    __tablename__ = "risk_assessments"

    assessment_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    entity_scope: Mapped[str] = mapped_column(String(32))
    target_id: Mapped[str] = mapped_column(String(128), index=True)
    time_window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    time_window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    score: Mapped[float] = mapped_column(Float)
    priority: Mapped[str] = mapped_column(String(16))
    generated_by: Mapped[str] = mapped_column(String(64))
    pathogen_pack_version: Mapped[str] = mapped_column(String(32))
    policy_pack_version: Mapped[str] = mapped_column(String(32))
    knowledge_bundle_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    triggering_rule_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    context_facts: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    signals_payload: Mapped[list[dict[str, Any]]] = mapped_column(JSON)


class PriorityAlertRecord(Base):
    __tablename__ = "priority_alerts"

    alert_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    assessment_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("risk_assessments.assessment_id"),
    )
    target_id: Mapped[str] = mapped_column(String(128), index=True)
    priority: Mapped[str] = mapped_column(String(16))
    summary: Mapped[str] = mapped_column(Text)
    signals_payload: Mapped[list[str]] = mapped_column(JSON)


class AuditRecordORM(Base):
    __tablename__ = "audit_records"

    audit_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    record_type: Mapped[str] = mapped_column(String(64))
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    actor: Mapped[str] = mapped_column(String(128))
    entity_type: Mapped[str] = mapped_column(String(64))
    entity_id: Mapped[str] = mapped_column(String(128), index=True)
    details: Mapped[dict[str, Any]] = mapped_column(JSON)
    schema_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    pathogen_pack_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    policy_pack_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    scoring_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    source_event_ids: Mapped[list[str]] = mapped_column(JSON)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)


class ProposedActionRecord(Base):
    __tablename__ = "proposed_actions"

    action_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    risk_assessment_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("risk_assessments.assessment_id"),
        nullable=True,
    )
    action_definition_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    action_type: Mapped[str] = mapped_column(String(64))
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    priority: Mapped[str | None] = mapped_column(String(16), nullable=True)
    execution_mode: Mapped[str] = mapped_column(String(32))
    target_scope: Mapped[str] = mapped_column(String(32))
    target_id: Mapped[str] = mapped_column(String(128), index=True)
    rationale: Mapped[str] = mapped_column(Text)
    required_reviewer_role: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32))
    constraints_applied: Mapped[list[str]] = mapped_column(JSON)
    knowledge_bundle_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    triggering_rule_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    audit_ref: Mapped[str] = mapped_column(String(36), ForeignKey("audit_records.audit_id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ReviewDecisionRecord(Base):
    __tablename__ = "review_decisions"

    decision_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    action_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposed_actions.action_id"))
    reviewer_role: Mapped[str] = mapped_column(String(64))
    decision: Mapped[str] = mapped_column(String(32))
    rationale: Mapped[str] = mapped_column(Text)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    audit_ref: Mapped[str] = mapped_column(String(36), ForeignKey("audit_records.audit_id"))


class KnowledgeBundleRecord(Base):
    __tablename__ = "knowledge_bundles"

    bundle_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    version: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    jurisdiction: Mapped[str] = mapped_column(String(64))
    organization: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)


class SourceDocumentRecord(Base):
    __tablename__ = "knowledge_source_documents"

    source_document_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    bundle_id: Mapped[str] = mapped_column(String(64), ForeignKey("knowledge_bundles.bundle_id"))
    title: Mapped[str] = mapped_column(String(255))
    organization: Mapped[str] = mapped_column(String(255))
    document_type: Mapped[str] = mapped_column(String(64))
    publication_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    version_label: Mapped[str | None] = mapped_column(String(64), nullable=True)
    jurisdiction: Mapped[str] = mapped_column(String(64))
    setting_scope: Mapped[list[str]] = mapped_column(JSON)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(String(16))
    machine_readability: Mapped[str] = mapped_column(String(32))
    ingestion_mode: Mapped[str] = mapped_column(String(32))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class PathogenPackRecord(Base):
    __tablename__ = "knowledge_pathogen_packs"

    pathogen_pack_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    bundle_id: Mapped[str] = mapped_column(String(64), ForeignKey("knowledge_bundles.bundle_id"))
    pathogen_code: Mapped[str] = mapped_column(String(64))
    display_name: Mapped[str] = mapped_column(String(255))
    version: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32))
    source_document_ids: Mapped[list[str]] = mapped_column(JSON)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class PolicyPackRecord(Base):
    __tablename__ = "knowledge_policy_packs"

    policy_pack_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    bundle_id: Mapped[str] = mapped_column(String(64), ForeignKey("knowledge_bundles.bundle_id"))
    name: Mapped[str] = mapped_column(String(255))
    version: Mapped[str] = mapped_column(String(32))
    jurisdiction: Mapped[str] = mapped_column(String(64))
    organization: Mapped[str] = mapped_column(String(255))
    source_document_ids: Mapped[list[str]] = mapped_column(JSON)


class ReviewWorkflowPackRecord(Base):
    __tablename__ = "knowledge_review_workflow_packs"

    workflow_pack_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    bundle_id: Mapped[str] = mapped_column(String(64), ForeignKey("knowledge_bundles.bundle_id"))
    name: Mapped[str] = mapped_column(String(255))
    version: Mapped[str] = mapped_column(String(32))
    source_document_ids: Mapped[list[str]] = mapped_column(JSON)


class ActionDefinitionRecord(Base):
    __tablename__ = "knowledge_action_definitions"

    action_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    bundle_id: Mapped[str] = mapped_column(String(64), ForeignKey("knowledge_bundles.bundle_id"))
    display_name: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(64))
    subtype: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(Text)
    pathogen_specificity: Mapped[list[str]] = mapped_column(JSON)
    execution_mode: Mapped[str] = mapped_column(String(32))
    requires_reviewer_role: Mapped[str] = mapped_column(String(64))
    target_scope: Mapped[str] = mapped_column(String(32))
    must_be_logged: Mapped[bool]


class EvidenceStatementRecord(Base):
    __tablename__ = "knowledge_evidence_statements"

    evidence_statement_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    bundle_id: Mapped[str] = mapped_column(String(64), ForeignKey("knowledge_bundles.bundle_id"))
    statement: Mapped[str] = mapped_column(Text)
    evidence_type: Mapped[str] = mapped_column(String(64))
    source_document_ids: Mapped[list[str]] = mapped_column(JSON)
    confidence: Mapped[str] = mapped_column(String(32))
    uncertainty_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    applies_to: Mapped[list[str]] = mapped_column(JSON)
    used_by_rule_ids: Mapped[list[str]] = mapped_column(JSON)


class TerminologyBindingRecord(Base):
    __tablename__ = "knowledge_terminology_bindings"

    binding_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    bundle_id: Mapped[str] = mapped_column(String(64), ForeignKey("knowledge_bundles.bundle_id"))
    local_system: Mapped[str] = mapped_column(String(64))
    local_code: Mapped[str] = mapped_column(String(64))
    local_display: Mapped[str] = mapped_column(String(255))
    canonical_field: Mapped[str] = mapped_column(String(128))
    canonical_value: Mapped[str] = mapped_column(String(128))


class RuleArtifactRecord(Base):
    __tablename__ = "knowledge_rule_artifacts"

    rule_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    bundle_id: Mapped[str] = mapped_column(String(64), ForeignKey("knowledge_bundles.bundle_id"))
    rule_kind: Mapped[str] = mapped_column(String(64), index=True)
    owner_pack_id: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[int]
    enabled: Mapped[bool]
    condition_payload: Mapped[dict[str, Any]] = mapped_column(JSON)
    outputs_payload: Mapped[list[dict[str, Any]]] = mapped_column(JSON)
    source_document_ids: Mapped[list[str]] = mapped_column(JSON)
    confidence: Mapped[str | None] = mapped_column(String(32), nullable=True)
    uncertainty_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    version: Mapped[str] = mapped_column(String(32))


class KnowledgeTestCaseRecord(Base):
    __tablename__ = "knowledge_test_cases"

    test_case_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    bundle_id: Mapped[str] = mapped_column(String(64), ForeignKey("knowledge_bundles.bundle_id"))
    name: Mapped[str] = mapped_column(String(255))
    input_facts: Mapped[dict[str, Any]] = mapped_column(JSON)
    expected_outputs: Mapped[list[dict[str, Any]]] = mapped_column(JSON)
    unexpected_outputs: Mapped[list[dict[str, Any]]] = mapped_column(JSON)
