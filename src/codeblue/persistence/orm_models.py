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
    action_type: Mapped[str] = mapped_column(String(64))
    target_scope: Mapped[str] = mapped_column(String(32))
    target_id: Mapped[str] = mapped_column(String(128), index=True)
    rationale: Mapped[str] = mapped_column(Text)
    required_reviewer_role: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32))
    constraints_applied: Mapped[list[str]] = mapped_column(JSON)
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
