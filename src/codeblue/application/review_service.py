from __future__ import annotations

from codeblue.domain.audit_models import ProvenanceRef
from codeblue.domain.governance_models import ActionStatus, ReviewDecision, ReviewDecisionType
from codeblue.persistence.repositories.audit_repository import AuditRepository
from codeblue.persistence.repositories.governance_repository import GovernanceRepository
from codeblue.services.audit import AuditService


STATUS_BY_DECISION: dict[ReviewDecisionType, ActionStatus] = {
    ReviewDecisionType.APPROVE: ActionStatus.APPROVED,
    ReviewDecisionType.REJECT: ActionStatus.REJECTED,
    ReviewDecisionType.OVERRIDE: ActionStatus.OVERRIDDEN,
    ReviewDecisionType.ESCALATE: ActionStatus.ESCALATED,
}


class ReviewService:
    def __init__(
        self,
        governance_repository: GovernanceRepository,
        audit_repository: AuditRepository,
        audit_service: AuditService,
    ) -> None:
        self.governance_repository = governance_repository
        self.audit_repository = audit_repository
        self.audit_service = audit_service

    def apply_decision(self, decision: ReviewDecision) -> ReviewDecision:
        self.governance_repository.update_action_status(
            str(decision.action_id),
            STATUS_BY_DECISION[decision.decision],
        )
        self.governance_repository.store_review_decision(decision)
        audit_record = self.audit_service.create_record(
            record_type="review_decision",
            actor=decision.reviewer_role,
            entity_type="proposed_action",
            entity_id=str(decision.action_id),
            details={"decision": decision.decision, "rationale": decision.rationale},
            provenance=ProvenanceRef(source_event_ids=[], explanation="Manual review decision."),
        )
        self.audit_repository.store(audit_record)
        return decision
