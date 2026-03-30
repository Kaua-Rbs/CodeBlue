from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from codeblue.domain.canonical_events import (
    EventEnvelope,
    EventType,
    PatientLocationEvent,
    StaffAssignmentEvent,
)
from codeblue.domain.state_models import (
    ExposureWindow,
    PatientState,
    RoomState,
    StaffState,
    StateSnapshotRef,
    TimeWindow,
    WardState,
)


def overlaps(left: TimeWindow, right: TimeWindow) -> bool:
    return left.start <= right.end and right.start <= left.end


class TemporalStateRebuilder:
    def build_patient_history(
        self,
        events: list[EventEnvelope],
        window_end: datetime,
    ) -> list[PatientState]:
        location_events = [
            event
            for event in sorted(events, key=lambda item: item.occurred_at)
            if event.event_type == EventType.PATIENT_LOCATION
        ]
        history: list[PatientState] = []
        grouped: dict[str, list[EventEnvelope]] = defaultdict(list)

        for event in location_events:
            payload = event.payload
            assert isinstance(payload, PatientLocationEvent)
            grouped[payload.patient_id].append(event)

        for patient_id, patient_events in grouped.items():
            for index, event in enumerate(patient_events):
                payload = event.payload
                assert isinstance(payload, PatientLocationEvent)
                next_event = patient_events[index + 1] if index + 1 < len(patient_events) else None
                history.append(
                    PatientState(
                        patient_id=patient_id,
                        room_id=payload.room_id,
                        ward_id=payload.ward_id,
                        start_at=event.occurred_at,
                        end_at=next_event.occurred_at if next_event else window_end,
                    )
                )

        return history

    def build_staff_history(
        self,
        events: list[EventEnvelope],
        window_end: datetime,
    ) -> list[StaffState]:
        assignment_events = [
            event
            for event in sorted(events, key=lambda item: item.occurred_at)
            if event.event_type == EventType.STAFF_ASSIGNMENT
        ]
        history: list[StaffState] = []
        grouped: dict[str, list[EventEnvelope]] = defaultdict(list)

        for event in assignment_events:
            payload = event.payload
            assert isinstance(payload, StaffAssignmentEvent)
            grouped[payload.staff_id].append(event)

        for staff_id, staff_events in grouped.items():
            for index, event in enumerate(staff_events):
                payload = event.payload
                assert isinstance(payload, StaffAssignmentEvent)
                next_event = staff_events[index + 1] if index + 1 < len(staff_events) else None
                history.append(
                    StaffState(
                        staff_id=staff_id,
                        ward_id=payload.ward_id,
                        role=payload.role,
                        room_id=payload.room_id,
                        start_at=event.occurred_at,
                        end_at=next_event.occurred_at if next_event else window_end,
                    )
                )

        return history

    def rebuild_snapshot(
        self,
        events: list[EventEnvelope],
        as_of: datetime,
    ) -> StateSnapshotRef:
        if not events:
            raise ValueError("At least one event is required to rebuild state.")

        ordered_events = sorted(events, key=lambda item: item.occurred_at)
        window = TimeWindow(start=ordered_events[0].occurred_at, end=as_of)
        patient_history = self.build_patient_history(ordered_events, as_of)
        staff_history = self.build_staff_history(ordered_events, as_of)

        active_patients = [
            state
            for state in patient_history
            if state.start_at <= as_of and (state.end_at is None or as_of <= state.end_at)
        ]
        active_staff = [
            state
            for state in staff_history
            if state.start_at <= as_of and (state.end_at is None or as_of <= state.end_at)
        ]

        room_states_map: dict[tuple[str, str], RoomState] = {}
        ward_states_map: dict[str, WardState] = {}

        for patient in active_patients:
            room_key = (patient.room_id, patient.ward_id)
            room_state = room_states_map.setdefault(
                room_key,
                RoomState(room_id=patient.room_id, ward_id=patient.ward_id),
            )
            room_state.active_patients.append(patient.patient_id)

            ward_state = ward_states_map.setdefault(
                patient.ward_id,
                WardState(ward_id=patient.ward_id),
            )
            if patient.room_id not in ward_state.room_ids:
                ward_state.room_ids.append(patient.room_id)
            ward_state.active_patients.append(patient.patient_id)

        for staff in active_staff:
            if staff.room_id:
                room_key = (staff.room_id, staff.ward_id)
                room_state = room_states_map.setdefault(
                    room_key,
                    RoomState(room_id=staff.room_id, ward_id=staff.ward_id),
                )
                room_state.active_staff.append(staff.staff_id)

            ward_state = ward_states_map.setdefault(
                staff.ward_id,
                WardState(ward_id=staff.ward_id),
            )
            ward_state.active_staff.append(staff.staff_id)

        return StateSnapshotRef(
            hospital_id=ordered_events[0].hospital_id,
            at=as_of,
            time_window=window,
            patient_states=active_patients,
            staff_states=active_staff,
            room_states=list(room_states_map.values()),
            ward_states=list(ward_states_map.values()),
            source_event_ids=[event.event_id for event in ordered_events if event.occurred_at <= as_of],
        )

    def exposure_windows(
        self,
        patients: list[PatientState],
        staff: list[StaffState],
    ) -> list[ExposureWindow]:
        windows: list[ExposureWindow] = []

        for patient in patients:
            patient_window = TimeWindow(
                start=patient.start_at,
                end=patient.end_at or patient.start_at,
            )
            for staff_member in staff:
                if staff_member.room_id != patient.room_id:
                    continue
                staff_window = TimeWindow(
                    start=staff_member.start_at,
                    end=staff_member.end_at or staff_member.start_at,
                )
                if overlaps(patient_window, staff_window):
                    windows.append(
                        ExposureWindow(
                            left_entity_id=patient.patient_id,
                            right_entity_id=staff_member.staff_id,
                            window=TimeWindow(
                                start=max(patient_window.start, staff_window.start),
                                end=min(patient_window.end, staff_window.end),
                            ),
                            reason=f"Shared room {patient.room_id}",
                        )
                    )

        return windows
