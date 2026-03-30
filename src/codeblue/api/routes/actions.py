from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from codeblue.api.schemas.reviews import ReviewActionRequest
from codeblue.application.review_service import ReviewService
from codeblue.domain.governance_models import ProposedAction, ReviewDecision
from codeblue.persistence.db import get_session
from codeblue.persistence.repositories.audit_repository import AuditRepository
from codeblue.persistence.repositories.governance_repository import GovernanceRepository
from codeblue.services.audit import AuditService

router = APIRouter(prefix="/actions", tags=["actions"])


@router.get("", response_model=list[ProposedAction])
def list_actions(session: Session = Depends(get_session)) -> list[ProposedAction]:
    return GovernanceRepository(session).list_actions()


@router.post("/{action_id}/review", response_model=ReviewDecision)
def review_action(
    action_id: str,
    request: ReviewActionRequest,
    session: Session = Depends(get_session),
) -> ReviewDecision:
    governance_repository = GovernanceRepository(session)
    action = governance_repository.get_action(action_id)
    if action is None:
        raise HTTPException(status_code=404, detail="Action not found.")

    decision = ReviewDecision(
        action_id=action.action_id,
        reviewer_role=request.reviewer_role,
        decision=request.decision,
        rationale=request.rationale,
        audit_ref=action.audit_ref,
    )
    review_service = ReviewService(
        governance_repository=governance_repository,
        audit_repository=AuditRepository(session),
        audit_service=AuditService(),
    )
    return review_service.apply_decision(decision)
