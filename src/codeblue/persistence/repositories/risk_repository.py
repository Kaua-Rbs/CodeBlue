from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from codeblue.domain.risk_models import PriorityAlert, RiskAssessment
from codeblue.persistence.orm_models import PriorityAlertRecord, RiskAssessmentRecord


class RiskRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def store_assessments(self, assessments: list[RiskAssessment]) -> list[RiskAssessment]:
        for assessment in assessments:
            self.session.add(
                RiskAssessmentRecord(
                    assessment_id=str(assessment.assessment_id),
                    entity_scope=assessment.entity_scope,
                    target_id=assessment.target_id,
                    time_window_start=assessment.time_window.start,
                    time_window_end=assessment.time_window.end,
                    score=assessment.score,
                    priority=assessment.priority,
                    generated_by=assessment.generated_by,
                    pathogen_pack_version=assessment.pathogen_pack_version,
                    policy_pack_version=assessment.policy_pack_version,
                    signals_payload=[
                        signal.model_dump(mode="json") for signal in assessment.contributing_signals
                    ],
                )
            )
        self.session.commit()
        return assessments

    def store_alerts(self, alerts: list[PriorityAlert]) -> list[PriorityAlert]:
        for alert in alerts:
            self.session.add(
                PriorityAlertRecord(
                    alert_id=str(alert.alert_id),
                    assessment_id=str(alert.assessment_id),
                    target_id=alert.target_id,
                    priority=alert.priority,
                    summary=alert.summary,
                    signals_payload=alert.top_signals,
                )
            )
        self.session.commit()
        return alerts

    def list_assessments(self) -> list[RiskAssessment]:
        records = self.session.scalars(
            select(RiskAssessmentRecord).order_by(RiskAssessmentRecord.time_window_start)
        ).all()
        return [
            RiskAssessment.model_validate(
                {
                    "assessment_id": record.assessment_id,
                    "entity_scope": record.entity_scope,
                    "target_id": record.target_id,
                    "time_window": {
                        "start": record.time_window_start,
                        "end": record.time_window_end,
                    },
                    "score": record.score,
                    "priority": record.priority,
                    "generated_by": record.generated_by,
                    "pathogen_pack_version": record.pathogen_pack_version,
                    "policy_pack_version": record.policy_pack_version,
                    "contributing_signals": record.signals_payload,
                }
            )
            for record in records
        ]

    def list_alerts(self) -> list[PriorityAlert]:
        records = self.session.scalars(select(PriorityAlertRecord)).all()
        return [
            PriorityAlert.model_validate(
                {
                    "alert_id": record.alert_id,
                    "assessment_id": record.assessment_id,
                    "target_id": record.target_id,
                    "priority": record.priority,
                    "summary": record.summary,
                    "top_signals": record.signals_payload,
                }
            )
            for record in records
        ]
