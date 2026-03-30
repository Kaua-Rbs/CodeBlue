from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class AuditModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class VersionRef(AuditModel):
    schema_version: str
    pathogen_pack_version: str
    policy_pack_version: str
    scoring_version: str


class ProvenanceRef(AuditModel):
    source_event_ids: list[UUID] = Field(default_factory=list)
    explanation: str | None = None


class ExplanationRef(AuditModel):
    summary: str
    supporting_event_ids: list[UUID] = Field(default_factory=list)


class AuditRecord(AuditModel):
    audit_id: UUID = Field(default_factory=uuid4)
    record_type: str
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    actor: str
    entity_type: str
    entity_id: str
    details: dict[str, Any] = Field(default_factory=dict)
    version_ref: VersionRef | None = None
    provenance: ProvenanceRef | None = None
