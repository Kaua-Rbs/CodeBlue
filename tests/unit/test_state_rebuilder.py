from __future__ import annotations

from datetime import UTC, datetime

from codeblue.application.state_rebuilder import TemporalStateRebuilder, overlaps
from codeblue.domain.state_models import TimeWindow
from tests.fixtures.demo_events import build_demo_events


def test_snapshot_rebuilds_active_patient_and_staff_state() -> None:
    events = build_demo_events()
    rebuilder = TemporalStateRebuilder()

    snapshot = rebuilder.rebuild_snapshot(
        events,
        as_of=datetime(2026, 3, 30, 11, 0, tzinfo=UTC),
    )

    assert len(snapshot.patient_states) == 1
    assert snapshot.patient_states[0].room_id == "room-101"
    assert len(snapshot.staff_states) == 1
    assert snapshot.staff_states[0].room_id == "room-101"
    assert snapshot.room_states[0].active_patients == ["patient-1"]


def test_overlap_helper_detects_intersection() -> None:
    left = TimeWindow(
        start=datetime(2026, 3, 30, 10, 0, tzinfo=UTC),
        end=datetime(2026, 3, 30, 11, 0, tzinfo=UTC),
    )
    right = TimeWindow(
        start=datetime(2026, 3, 30, 10, 30, tzinfo=UTC),
        end=datetime(2026, 3, 30, 12, 0, tzinfo=UTC),
    )

    assert overlaps(left, right) is True
