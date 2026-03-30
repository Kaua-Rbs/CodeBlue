from __future__ import annotations

from datetime import UTC, datetime

from codeblue.domain.canonical_events import EventEnvelope, EventType


def build_demo_events() -> list[EventEnvelope]:
    return [
        EventEnvelope.model_validate(
            {
                "event_type": EventType.PATIENT_LOCATION,
                "occurred_at": datetime(2026, 3, 30, 10, 0, tzinfo=UTC),
                "recorded_at": datetime(2026, 3, 30, 10, 0, tzinfo=UTC),
                "source_system": "demo_emr",
                "hospital_id": "hospital-a",
                "payload": {
                    "event_type": EventType.PATIENT_LOCATION,
                    "patient_id": "patient-1",
                    "room_id": "room-101",
                    "ward_id": "ward-a",
                },
            }
        ),
        EventEnvelope.model_validate(
            {
                "event_type": EventType.STAFF_ASSIGNMENT,
                "occurred_at": datetime(2026, 3, 30, 10, 30, tzinfo=UTC),
                "recorded_at": datetime(2026, 3, 30, 10, 30, tzinfo=UTC),
                "source_system": "demo_emr",
                "hospital_id": "hospital-a",
                "payload": {
                    "event_type": EventType.STAFF_ASSIGNMENT,
                    "staff_id": "staff-1",
                    "ward_id": "ward-a",
                    "room_id": "room-101",
                    "role": "nurse",
                },
            }
        ),
        EventEnvelope.model_validate(
            {
                "event_type": EventType.LAB_CONFIRMATION,
                "occurred_at": datetime(2026, 3, 30, 11, 0, tzinfo=UTC),
                "recorded_at": datetime(2026, 3, 30, 11, 5, tzinfo=UTC),
                "source_system": "demo_lab",
                "hospital_id": "hospital-a",
                "payload": {
                    "event_type": EventType.LAB_CONFIRMATION,
                    "subject_type": "patient",
                    "subject_id": "patient-1",
                    "pathogen_code": "demo-flu",
                    "result": "positive",
                },
            }
        ),
    ]
