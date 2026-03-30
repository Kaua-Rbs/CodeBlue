from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from codeblue.domain.risk_models import PriorityAlert, RiskAssessment
from codeblue.persistence.db import get_session
from codeblue.persistence.repositories.risk_repository import RiskRepository

router = APIRouter(prefix="/risk", tags=["risk"])


@router.get("/assessments", response_model=list[RiskAssessment])
def list_assessments(session: Session = Depends(get_session)) -> list[RiskAssessment]:
    return RiskRepository(session).list_assessments()


@router.get("/alerts", response_model=list[PriorityAlert])
def list_alerts(session: Session = Depends(get_session)) -> list[PriorityAlert]:
    return RiskRepository(session).list_alerts()
