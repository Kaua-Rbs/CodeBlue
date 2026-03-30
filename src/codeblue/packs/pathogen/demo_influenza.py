from __future__ import annotations

from collections import defaultdict
from uuid import UUID

from codeblue.domain.canonical_events import (
    EventEnvelope,
    EventType,
    LabConfirmationEvent,
    SuspectedCaseEvent,
)
from codeblue.domain.risk_models import (
    EntityScope,
    PriorityAlert,
    RiskAssessment,
    RiskPriority,
    RiskSignal,
)
from codeblue.domain.state_models import StateSnapshotRef, TimeWindow
from codeblue.packs.pathogen.base import PathogenPack


def _priority_for_score(score: float) -> RiskPriority:
    if score >= 0.9:
        return RiskPriority.CRITICAL
    if score >= 0.7:
        return RiskPriority.HIGH
    if score >= 0.4:
        return RiskPriority.MEDIUM
    return RiskPriority.LOW


class DemoInfluenzaPathogenPack(PathogenPack):
    pack_id = "demo_influenza"
    name = "Demo Influenza-Like Pathogen Pack"
    version = "0.1.0"

    def assess(
        self,
        events: list[EventEnvelope],
        snapshot: StateSnapshotRef,
        time_window: TimeWindow,
        policy_pack_version: str,
        scoring_version: str,
    ) -> tuple[list[RiskAssessment], list[PriorityAlert]]:
        positive_patients: set[str] = set()
        suspected_patients: set[str] = set()
        evidence_by_patient: dict[str, list[UUID]] = defaultdict(list)

        for event in events:
            if event.occurred_at > snapshot.at:
                continue
            if event.event_type == EventType.LAB_CONFIRMATION:
                payload = event.payload
                assert isinstance(payload, LabConfirmationEvent)
                if payload.subject_type == "patient" and payload.result == "positive":
                    positive_patients.add(payload.subject_id)
                    evidence_by_patient[payload.subject_id].append(event.event_id)
            elif event.event_type == EventType.SUSPECTED_CASE:
                payload = event.payload
                assert isinstance(payload, SuspectedCaseEvent)
                if payload.subject_type == "patient":
                    suspected_patients.add(payload.subject_id)
                    evidence_by_patient[payload.subject_id].append(event.event_id)

        assessments: list[RiskAssessment] = []
        alerts: list[PriorityAlert] = []

        for room_state in snapshot.room_states:
            positive_count = sum(
                1 for patient_id in room_state.active_patients if patient_id in positive_patients
            )
            suspected_count = sum(
                1 for patient_id in room_state.active_patients if patient_id in suspected_patients
            )
            if positive_count == 0 and suspected_count == 0:
                continue

            score = min(1.0, (positive_count * 0.6) + (suspected_count * 0.3) + 0.1)
            priority = _priority_for_score(score)
            signals = [
                RiskSignal(
                    name="positive_cases",
                    value=float(positive_count),
                    weight=0.6,
                    evidence_event_ids=[
                        event_id
                        for patient_id in room_state.active_patients
                        for event_id in evidence_by_patient[patient_id]
                    ],
                    explanation=f"{positive_count} confirmed positive patient(s) in room.",
                ),
                RiskSignal(
                    name="suspected_cases",
                    value=float(suspected_count),
                    weight=0.3,
                    evidence_event_ids=[
                        event_id
                        for patient_id in room_state.active_patients
                        for event_id in evidence_by_patient[patient_id]
                    ],
                    explanation=f"{suspected_count} suspected patient(s) in room.",
                ),
            ]
            assessment = RiskAssessment(
                entity_scope=EntityScope.ROOM,
                target_id=room_state.room_id,
                time_window=time_window,
                score=score,
                priority=priority,
                contributing_signals=signals,
                generated_by=scoring_version,
                pathogen_pack_version=self.version,
                policy_pack_version=policy_pack_version,
            )
            assessments.append(assessment)
            alerts.append(
                PriorityAlert(
                    assessment_id=assessment.assessment_id,
                    target_id=room_state.room_id,
                    priority=priority,
                    summary=f"Room {room_state.room_id} has elevated outbreak risk.",
                    top_signals=[signal.name for signal in signals if signal.value > 0],
                )
            )

        for ward_state in snapshot.ward_states:
            impacted_rooms = [
                assessment for assessment in assessments if assessment.target_id in ward_state.room_ids
            ]
            if not impacted_rooms:
                continue
            score = max(assessment.score for assessment in impacted_rooms)
            priority = _priority_for_score(score)
            signal = RiskSignal(
                name="impacted_rooms",
                value=float(len(impacted_rooms)),
                weight=0.5,
                evidence_event_ids=[],
                explanation=f"{len(impacted_rooms)} room(s) in the ward have elevated risk.",
            )
            assessment = RiskAssessment(
                entity_scope=EntityScope.WARD,
                target_id=ward_state.ward_id,
                time_window=time_window,
                score=score,
                priority=priority,
                contributing_signals=[signal],
                generated_by=scoring_version,
                pathogen_pack_version=self.version,
                policy_pack_version=policy_pack_version,
            )
            assessments.append(assessment)
            alerts.append(
                PriorityAlert(
                    assessment_id=assessment.assessment_id,
                    target_id=ward_state.ward_id,
                    priority=priority,
                    summary=f"Ward {ward_state.ward_id} requires outbreak review.",
                    top_signals=[signal.name],
                )
            )

        return assessments, alerts
