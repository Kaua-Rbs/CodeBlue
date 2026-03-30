from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StateModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TimeWindow(StateModel):
    start: datetime
    end: datetime

    @model_validator(mode="after")
    def validate_bounds(self) -> "TimeWindow":
        if self.end < self.start:
            raise ValueError("TimeWindow.end must be greater than or equal to TimeWindow.start.")
        return self


class PatientState(StateModel):
    patient_id: str
    room_id: str
    ward_id: str
    start_at: datetime
    end_at: datetime | None = None


class StaffState(StateModel):
    staff_id: str
    ward_id: str
    role: str
    room_id: str | None = None
    start_at: datetime
    end_at: datetime | None = None


class RoomState(StateModel):
    room_id: str
    ward_id: str
    active_patients: list[str] = Field(default_factory=list)
    active_staff: list[str] = Field(default_factory=list)


class WardState(StateModel):
    ward_id: str
    room_ids: list[str] = Field(default_factory=list)
    active_patients: list[str] = Field(default_factory=list)
    active_staff: list[str] = Field(default_factory=list)


class ExposureWindow(StateModel):
    left_entity_id: str
    right_entity_id: str
    window: TimeWindow
    reason: str


class StateSnapshotRef(StateModel):
    hospital_id: str
    at: datetime
    time_window: TimeWindow
    patient_states: list[PatientState]
    staff_states: list[StaffState]
    room_states: list[RoomState]
    ward_states: list[WardState]
    source_event_ids: list[UUID]
