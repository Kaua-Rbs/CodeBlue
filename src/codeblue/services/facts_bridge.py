from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Any

from codeblue.domain.canonical_events import (
    EventEnvelope,
    EventType,
    LabConfirmationEvent,
    PatientLocationEvent,
    RoomMetadataEvent,
)
from codeblue.domain.risk_models import RiskAssessment
from codeblue.domain.state_models import PatientState, StateSnapshotRef


class KnowledgeFactsBridge:
    def patient_facts(
        self,
        events: list[EventEnvelope],
        snapshot: StateSnapshotRef,
        patient_state: PatientState,
    ) -> dict[str, Any]:
        latest_confirmed_pathogen: str | None = None
        earliest_admission_at: datetime | None = None
        room_type = "standard"

        for event in sorted(events, key=lambda item: item.occurred_at):
            if event.occurred_at > snapshot.at:
                continue
            if event.event_type == EventType.LAB_CONFIRMATION:
                payload = event.payload
                assert isinstance(payload, LabConfirmationEvent)
                if payload.subject_type == "patient" and payload.subject_id == patient_state.patient_id:
                    if payload.result == "positive":
                        latest_confirmed_pathogen = payload.pathogen_code
            elif event.event_type == EventType.PATIENT_LOCATION:
                payload = event.payload
                assert isinstance(payload, PatientLocationEvent)
                if payload.patient_id == patient_state.patient_id and earliest_admission_at is None:
                    earliest_admission_at = event.occurred_at
            elif event.event_type == EventType.ROOM_METADATA:
                payload = event.payload
                assert isinstance(payload, RoomMetadataEvent)
                if payload.room_id == patient_state.room_id:
                    room_type = payload.room_type

        hours_since_admission = 0.0
        if earliest_admission_at is not None:
            delta = snapshot.at - earliest_admission_at
            hours_since_admission = delta.total_seconds() / 3600

        return {
            "lab.confirmed_pathogen": latest_confirmed_pathogen,
            "encounter.hours_since_admission": hours_since_admission,
            "patient.id": patient_state.patient_id,
            "room.id": patient_state.room_id,
            "room.type": room_type,
            "ward.id": patient_state.ward_id,
        }

    def assessment_facts(self, assessment: RiskAssessment) -> dict[str, Any]:
        facts = dict(assessment.context_facts)
        facts["assessment.priority"] = assessment.priority
        facts["assessment.target_id"] = assessment.target_id
        return facts

    def action_facts(
        self,
        action_category: str | None,
        execution_mode: str,
        action_definition_id: str | None = None,
    ) -> dict[str, Any]:
        return {
            "proposed_action.category": action_category,
            "proposed_action.execution_mode": execution_mode,
            "proposed_action.action_definition_id": action_definition_id,
        }

    def overlap_facts(
        self,
        left_room_id: str,
        right_room_id: str,
        duration_hours: float,
    ) -> dict[str, Any]:
        return {
            "overlap.same_room": left_room_id == right_room_id,
            "overlap.duration_hours": duration_hours,
        }

    def count_values(self, values: Iterable[object]) -> int:
        return sum(1 for _ in values)
