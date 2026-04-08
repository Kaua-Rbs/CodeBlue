from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Annotated, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EventType(StrEnum):
    PATIENT_LOCATION = "patient_location"
    STAFF_ASSIGNMENT = "staff_assignment"
    LAB_CONFIRMATION = "lab_confirmation"
    SUSPECTED_CASE = "suspected_case"
    WARD_METADATA = "ward_metadata"
    ROOM_METADATA = "room_metadata"
    ADJACENCY_EDGE = "adjacency_edge"
    INTERVENTION = "intervention"


class CanonicalModel(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)


class PatientLocationEvent(CanonicalModel):
    event_type: Literal[EventType.PATIENT_LOCATION]
    patient_id: str
    room_id: str
    ward_id: str
    bed_id: str | None = None


class StaffAssignmentEvent(CanonicalModel):
    event_type: Literal[EventType.STAFF_ASSIGNMENT]
    staff_id: str
    ward_id: str
    room_id: str | None = None
    role: str


class LabConfirmationEvent(CanonicalModel):
    event_type: Literal[EventType.LAB_CONFIRMATION]
    subject_type: Literal["patient", "staff"]
    subject_id: str
    pathogen_code: str
    result: Literal["positive", "negative", "inconclusive"]
    specimen_collected_at: datetime | None = None


class SuspectedCaseEvent(CanonicalModel):
    event_type: Literal[EventType.SUSPECTED_CASE]
    subject_type: Literal["patient", "staff"]
    subject_id: str
    suspicion_level: Literal["low", "medium", "high"]
    reason: str


class WardMetadataEvent(CanonicalModel):
    event_type: Literal[EventType.WARD_METADATA]
    ward_id: str
    name: str
    capacity: int
    contains_isolation_rooms: bool = False


class RoomMetadataEvent(CanonicalModel):
    event_type: Literal[EventType.ROOM_METADATA]
    room_id: str
    ward_id: str
    room_type: str = "standard"
    capacity: int = 1


class AdjacencyEdgeEvent(CanonicalModel):
    event_type: Literal[EventType.ADJACENCY_EDGE]
    from_room_id: str
    to_room_id: str
    relationship: str = "adjacent"


class InterventionEvent(CanonicalModel):
    event_type: Literal[EventType.INTERVENTION]
    action_type: str
    target_scope: str
    target_id: str
    status: str
    notes: str | None = None


EventPayload = Annotated[
    PatientLocationEvent
    | StaffAssignmentEvent
    | LabConfirmationEvent
    | SuspectedCaseEvent
    | WardMetadataEvent
    | RoomMetadataEvent
    | AdjacencyEdgeEvent
    | InterventionEvent,
    Field(discriminator="event_type"),
]


class EventEnvelope(CanonicalModel):
    event_id: UUID = Field(default_factory=uuid4)
    event_type: EventType
    occurred_at: datetime
    recorded_at: datetime
    source_system: str
    hospital_id: str
    payload: EventPayload
    schema_version: str = "1.0.0"

    @model_validator(mode="after")
    def validate_event_type(self) -> EventEnvelope:
        if self.event_type != self.payload.event_type:
            message = (
                f"Envelope event_type '{self.event_type}' does not match payload "
                f"event_type '{self.payload.event_type}'."
            )
            raise ValueError(message)
        if self.recorded_at < self.occurred_at:
            raise ValueError("recorded_at must be greater than or equal to occurred_at.")
        return self
