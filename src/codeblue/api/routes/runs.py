from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from codeblue.application.orchestrator import OutbreakOrchestrator
from codeblue.packs.pathogen.demo_influenza import DemoInfluenzaPathogenPack
from codeblue.packs.policy.demo_hospital_policy import DemoHospitalPolicyPack
from codeblue.persistence.db import get_session
from codeblue.persistence.repositories.event_repository import EventRepository

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("")
def trigger_run(session: Session = Depends(get_session)) -> dict[str, object]:
    events = EventRepository(session).list_all()
    if not events:
        raise HTTPException(status_code=400, detail="No events are available to run.")

    orchestrator = OutbreakOrchestrator(
        session=session,
        pathogen_pack=DemoInfluenzaPathogenPack(),
        policy_pack=DemoHospitalPolicyPack(),
    )
    result = orchestrator.run(events)
    return {
        "snapshot_at": result.snapshot_at,
        "assessment_count": len(result.assessments),
        "alert_count": len(result.alerts),
        "action_count": len(result.actions),
    }
