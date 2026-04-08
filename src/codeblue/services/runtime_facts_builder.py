from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

from codeblue.domain.canonical_events import (
    EventEnvelope,
    EventType,
    LabConfirmationEvent,
    PatientLocationEvent,
    SuspectedCaseEvent,
)
from codeblue.domain.knowledge_runtime_models import DeploymentProfile
from codeblue.domain.state_models import PatientState, StateSnapshotRef
from codeblue.services.deployment_profile_service import DeploymentProfileService

RESPIRATORY_KEYWORDS = (
    "influenza",
    "flu",
    "respiratory",
    "cough",
    "fever",
    "sore throat",
    "runny nose",
    "myalgia",
)
ARRIVAL_WINDOW = timedelta(hours=6)


class RuntimeFactsBuilder:
    def __init__(self) -> None:
        self.deployment_profile_service = DeploymentProfileService()

    def build(
        self,
        events: list[EventEnvelope],
        snapshot: StateSnapshotRef,
        deployment_profile: DeploymentProfile | None,
    ) -> dict[str, Any]:
        sorted_events = sorted(events, key=lambda item: item.occurred_at)
        patient_by_id = {patient.patient_id: patient for patient in snapshot.patient_states}
        admission_by_patient = self._earliest_admission_times(sorted_events)
        respiratory_arrival = self._symptomatic_arrival_facts(
            sorted_events,
            patient_by_id,
            admission_by_patient,
        )
        inpatient_influenza = self._inpatient_influenza_facts(
            sorted_events,
            patient_by_id,
            admission_by_patient,
        )
        ward_cluster = self._ward_cluster_facts(patient_by_id, inpatient_influenza)
        seasonality = self.deployment_profile_service.seasonality_flags(
            deployment_profile,
            snapshot.at.date(),
        )

        return {
            "seasonality.prealert_active": {
                "matched": seasonality["seasonality.prealert_active"],
                "month": snapshot.at.strftime("%B"),
            },
            "seasonality.high_alert_active": {
                "matched": seasonality["seasonality.high_alert_active"],
                "month": snapshot.at.strftime("%B"),
            },
            "symptoms.present_at_arrival": respiratory_arrival,
            "case.suspected_or_confirmed_influenza": inpatient_influenza,
            "ward.cluster_signal": ward_cluster,
        }

    def _earliest_admission_times(
        self,
        events: list[EventEnvelope],
    ) -> dict[str, datetime]:
        admission_by_patient: dict[str, datetime] = {}
        for event in events:
            if event.event_type != EventType.PATIENT_LOCATION:
                continue
            payload = event.payload
            assert isinstance(payload, PatientLocationEvent)
            admission_by_patient.setdefault(payload.patient_id, event.occurred_at)
        return admission_by_patient

    def _symptomatic_arrival_facts(
        self,
        events: list[EventEnvelope],
        patient_by_id: dict[str, PatientState],
        admission_by_patient: dict[str, datetime],
    ) -> dict[str, dict[str, Any]]:
        matches: dict[str, dict[str, Any]] = {}
        for event in events:
            if event.event_type != EventType.SUSPECTED_CASE:
                continue
            payload = event.payload
            assert isinstance(payload, SuspectedCaseEvent)
            if payload.subject_type != "patient":
                continue
            patient_state = patient_by_id.get(payload.subject_id)
            admission_at = admission_by_patient.get(payload.subject_id)
            if patient_state is None or admission_at is None:
                continue
            if event.occurred_at - admission_at > ARRIVAL_WINDOW:
                continue
            if not self._looks_respiratory(payload.reason):
                continue
            matches[payload.subject_id] = {
                "matched": True,
                "reason": payload.reason,
                "suspicion_level": payload.suspicion_level,
                "detected_at": event.occurred_at.isoformat(),
                "admission_at": admission_at.isoformat(),
                "ward_id": patient_state.ward_id,
                "room_id": patient_state.room_id,
            }
        return matches

    def _inpatient_influenza_facts(
        self,
        events: list[EventEnvelope],
        patient_by_id: dict[str, PatientState],
        admission_by_patient: dict[str, datetime],
    ) -> dict[str, dict[str, Any]]:
        matches: dict[str, dict[str, Any]] = {}
        for event in events:
            admission_at: datetime | None = None
            patient_state: PatientState | None = None
            if event.event_type == EventType.LAB_CONFIRMATION:
                payload = event.payload
                assert isinstance(payload, LabConfirmationEvent)
                if payload.subject_type != "patient" or payload.result != "positive":
                    continue
                if not self._looks_like_influenza(payload.pathogen_code):
                    continue
                patient_state = patient_by_id.get(payload.subject_id)
                admission_at = admission_by_patient.get(payload.subject_id)
                if (
                    patient_state is None
                    or admission_at is None
                    or event.occurred_at < admission_at
                ):
                    continue
                matches[payload.subject_id] = {
                    "matched": True,
                    "source": "lab_confirmation",
                    "pathogen_code": payload.pathogen_code,
                    "detected_at": event.occurred_at.isoformat(),
                    "admission_at": admission_at.isoformat(),
                    "ward_id": patient_state.ward_id,
                    "room_id": patient_state.room_id,
                }
            elif event.event_type == EventType.SUSPECTED_CASE:
                payload = event.payload
                assert isinstance(payload, SuspectedCaseEvent)
                if payload.subject_type != "patient":
                    continue
                if not self._looks_respiratory(payload.reason):
                    continue
                patient_state = patient_by_id.get(payload.subject_id)
                admission_at = admission_by_patient.get(payload.subject_id)
                if (
                    patient_state is None
                    or admission_at is None
                    or event.occurred_at < admission_at
                ):
                    continue
                matches.setdefault(
                    payload.subject_id,
                    {
                        "matched": True,
                        "source": "suspected_case",
                        "reason": payload.reason,
                        "suspicion_level": payload.suspicion_level,
                        "detected_at": event.occurred_at.isoformat(),
                        "admission_at": admission_at.isoformat(),
                        "ward_id": patient_state.ward_id,
                        "room_id": patient_state.room_id,
                    },
                )
        return matches

    def _ward_cluster_facts(
        self,
        patient_by_id: dict[str, PatientState],
        inpatient_influenza: dict[str, dict[str, Any]],
    ) -> dict[str, dict[str, Any]]:
        cluster_patients: dict[str, list[str]] = defaultdict(list)
        for patient_id in inpatient_influenza:
            patient_state = patient_by_id.get(patient_id)
            if patient_state is None:
                continue
            cluster_patients[patient_state.ward_id].append(patient_id)

        return {
            ward_id: {
                "matched": True,
                "patient_ids": sorted(patient_ids),
                "count": len(patient_ids),
            }
            for ward_id, patient_ids in cluster_patients.items()
            if len(patient_ids) >= 2
        }

    def _looks_respiratory(self, value: str | None) -> bool:
        text = (value or "").lower()
        return any(keyword in text for keyword in RESPIRATORY_KEYWORDS)

    def _looks_like_influenza(self, value: str | None) -> bool:
        text = (value or "").lower()
        return "influenza" in text or "flu" in text
