from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from codeblue.domain.governance_models import ActionStatus, ProposedAction, ReviewDecision
from codeblue.persistence.orm_models import ProposedActionRecord, ReviewDecisionRecord


class GovernanceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def store_actions(self, actions: list[ProposedAction]) -> list[ProposedAction]:
        for action in actions:
            self.session.add(
                ProposedActionRecord(
                    action_id=str(action.action_id),
                    risk_assessment_id=(
                        str(action.risk_assessment_id) if action.risk_assessment_id else None
                    ),
                    action_definition_id=action.action_definition_id,
                    action_type=action.action_type,
                    category=action.category,
                    priority=action.priority,
                    execution_mode=action.execution_mode,
                    target_scope=action.target_scope,
                    target_id=action.target_id,
                    rationale=action.rationale,
                    required_reviewer_role=action.required_reviewer_role,
                    status=action.status,
                    constraints_applied=action.constraints_applied,
                    knowledge_bundle_id=action.knowledge_bundle_id,
                    triggering_rule_ids=action.triggering_rule_ids,
                    audit_ref=str(action.audit_ref),
                    created_at=action.created_at,
                )
            )
        self.session.commit()
        return actions

    def list_actions(self) -> list[ProposedAction]:
        records = self.session.scalars(
            select(ProposedActionRecord).order_by(ProposedActionRecord.created_at)
        ).all()
        return [
            ProposedAction.model_validate(
                {
                    "action_id": record.action_id,
                    "risk_assessment_id": record.risk_assessment_id,
                    "action_definition_id": record.action_definition_id,
                    "action_type": record.action_type,
                    "category": record.category,
                    "priority": record.priority,
                    "execution_mode": record.execution_mode,
                    "target_scope": record.target_scope,
                    "target_id": record.target_id,
                    "rationale": record.rationale,
                    "required_reviewer_role": record.required_reviewer_role,
                    "status": record.status,
                    "constraints_applied": record.constraints_applied,
                    "knowledge_bundle_id": record.knowledge_bundle_id,
                    "triggering_rule_ids": record.triggering_rule_ids,
                    "audit_ref": record.audit_ref,
                    "created_at": record.created_at,
                }
            )
            for record in records
        ]

    def get_action(self, action_id: str) -> ProposedActionRecord | None:
        return self.session.get(ProposedActionRecord, action_id)

    def clear_actions_and_reviews(self) -> None:
        self.session.execute(delete(ReviewDecisionRecord))
        self.session.execute(delete(ProposedActionRecord))
        self.session.commit()

    def update_action_status(self, action_id: str, status: ActionStatus) -> ProposedActionRecord:
        record = self.session.get(ProposedActionRecord, action_id)
        if record is None:
            raise ValueError(f"Action '{action_id}' was not found.")
        record.status = status
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def store_review_decision(self, decision: ReviewDecision) -> ReviewDecision:
        self.session.add(
            ReviewDecisionRecord(
                decision_id=str(decision.decision_id),
                action_id=str(decision.action_id),
                reviewer_role=decision.reviewer_role,
                decision=decision.decision,
                rationale=decision.rationale,
                decided_at=decision.decided_at,
                audit_ref=str(decision.audit_ref),
            )
        )
        self.session.commit()
        return decision
