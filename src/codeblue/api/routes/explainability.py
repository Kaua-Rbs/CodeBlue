from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from codeblue.persistence.db import get_session
from codeblue.persistence.repositories.audit_repository import AuditRepository
from codeblue.persistence.repositories.governance_repository import GovernanceRepository
from codeblue.persistence.repositories.risk_repository import RiskRepository
from codeblue.services.explanation import build_action_explanation

router = APIRouter(prefix="/explainability", tags=["explainability"])


@router.get("/actions/{action_id}")
def explain_action(
    action_id: str,
    session: Session = Depends(get_session),
) -> dict[str, object]:
    governance_repository = GovernanceRepository(session)
    action_record = governance_repository.get_action(action_id)
    if action_record is None:
        raise HTTPException(status_code=404, detail="Action not found.")

    actions = governance_repository.list_actions()
    matching_action = next((item for item in actions if str(item.action_id) == action_id), None)
    if matching_action is None:
        raise HTTPException(status_code=404, detail="Action not found.")

    assessments = RiskRepository(session).list_assessments()
    assessment = next(
        (
            item
            for item in assessments
            if matching_action.risk_assessment_id
            and str(item.assessment_id) == str(matching_action.risk_assessment_id)
        ),
        None,
    )
    audit_record = AuditRepository(session).get_record(str(matching_action.audit_ref))
    trace = None
    if audit_record is not None:
        trace = audit_record.details.get("trace")
    return {
        "action_id": action_id,
        "explanation": build_action_explanation(matching_action, assessment, trace),
        "assessment_id": str(assessment.assessment_id) if assessment else None,
        "trace": trace,
    }
