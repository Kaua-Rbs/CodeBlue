from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from codeblue.domain.state_models import TimeWindow


class RiskModel(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)


class EntityScope(StrEnum):
    PATIENT = "patient"
    ROOM = "room"
    WARD = "ward"
    STAFF_BRIDGE = "staff_bridge"
    HOSPITAL = "hospital"


class RiskPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskSignal(RiskModel):
    name: str
    value: float
    weight: float
    evidence_event_ids: list[UUID] = Field(default_factory=list)
    explanation: str


class SpilloverEstimate(RiskModel):
    estimate_id: UUID = Field(default_factory=uuid4)
    source_ward_id: str
    target_ward_id: str
    time_window: TimeWindow
    likelihood: float
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class RiskAssessment(RiskModel):
    assessment_id: UUID = Field(default_factory=uuid4)
    entity_scope: EntityScope
    target_id: str
    time_window: TimeWindow
    score: float
    priority: RiskPriority
    contributing_signals: list[RiskSignal]
    generated_by: str
    pathogen_pack_version: str
    policy_pack_version: str
    knowledge_bundle_id: str | None = None
    triggering_rule_ids: list[str] = Field(default_factory=list)
    context_facts: dict[str, Any] = Field(default_factory=dict)


class PriorityAlert(RiskModel):
    alert_id: UUID = Field(default_factory=uuid4)
    assessment_id: UUID
    target_id: str
    priority: RiskPriority
    summary: str
    top_signals: list[str]
