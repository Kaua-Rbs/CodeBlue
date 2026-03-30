from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class GovernanceModel(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)


class ActionStatus(StrEnum):
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    OVERRIDDEN = "overridden"
    ESCALATED = "escalated"


class TargetScope(StrEnum):
    PATIENT = "patient"
    ROOM = "room"
    WARD = "ward"
    STAFF = "staff"
    PHARMACY = "pharmacy"
    IPC_TEAM = "ipc_team"


class ReviewDecisionType(StrEnum):
    APPROVE = "approve"
    REJECT = "reject"
    OVERRIDE = "override"
    ESCALATE = "escalate"


class ProposedAction(GovernanceModel):
    action_id: UUID = Field(default_factory=uuid4)
    risk_assessment_id: UUID | None = None
    action_type: str
    target_scope: TargetScope
    target_id: str
    rationale: str
    required_reviewer_role: str
    status: ActionStatus = ActionStatus.PENDING_REVIEW
    constraints_applied: list[str] = Field(default_factory=list)
    audit_ref: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ActionReviewRequest(GovernanceModel):
    action_id: UUID
    requested_role: str
    submitted_at: datetime = Field(default_factory=datetime.utcnow)


class ReviewDecision(GovernanceModel):
    decision_id: UUID = Field(default_factory=uuid4)
    action_id: UUID
    reviewer_role: str
    decision: ReviewDecisionType
    rationale: str
    decided_at: datetime = Field(default_factory=datetime.utcnow)
    audit_ref: UUID


class EscalationRecord(GovernanceModel):
    escalation_id: UUID = Field(default_factory=uuid4)
    action_id: UUID
    from_role: str
    to_role: str
    reason: str
    escalated_at: datetime = Field(default_factory=datetime.utcnow)
