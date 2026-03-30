from __future__ import annotations

from datetime import UTC, datetime

import pytest

from codeblue.domain.canonical_events import EventEnvelope, EventType


def test_event_envelope_requires_matching_payload_type() -> None:
    with pytest.raises(ValueError):
        EventEnvelope.model_validate(
            {
                "event_type": EventType.PATIENT_LOCATION,
                "occurred_at": datetime(2026, 3, 30, 10, 0, tzinfo=UTC),
                "recorded_at": datetime(2026, 3, 30, 10, 1, tzinfo=UTC),
                "source_system": "demo_emr",
                "hospital_id": "hospital-a",
                "payload": {
                    "event_type": EventType.STAFF_ASSIGNMENT,
                    "staff_id": "staff-1",
                    "ward_id": "ward-a",
                    "role": "nurse",
                },
            }
        )


def test_event_envelope_preserves_payload_shape() -> None:
    event = EventEnvelope.model_validate(
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
    )

    assert event.payload.patient_id == "patient-1"
