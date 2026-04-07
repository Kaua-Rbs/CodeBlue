from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from codeblue.application.orchestrator import OutbreakOrchestrator
from codeblue.packs.pathogen.compiled_workbook_pathogen import CompiledWorkbookPathogenPack
from codeblue.packs.pathogen.demo_influenza import DemoInfluenzaPathogenPack
from codeblue.packs.policy.compiled_workbook_policy import CompiledWorkbookPolicyPack
from codeblue.packs.policy.demo_hospital_policy import DemoHospitalPolicyPack
from codeblue.persistence.db import get_session
from codeblue.persistence.repositories.event_repository import EventRepository
from codeblue.persistence.repositories.knowledge_repository import KnowledgeRepository
from codeblue.services.compiled_runtime_loader import load_compiled_runtime_package_cached
from codeblue.services.knowledge_loader import ensure_demo_knowledge_bundle
from codeblue.services.policy_execution_context_builder import CompiledPolicyExecutionContextBuilder

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("")
def trigger_run(session: Session = Depends(get_session)) -> dict[str, object]:
    events = EventRepository(session).list_all()
    if not events:
        raise HTTPException(status_code=400, detail="No events are available to run.")
    try:
        compiled_package = load_compiled_runtime_package_cached()
        KnowledgeRepository(session).replace_bundle(compiled_package.knowledge_bundle)
        orchestrator = OutbreakOrchestrator(
            session=session,
            pathogen_pack=CompiledWorkbookPathogenPack(),
            policy_pack=CompiledWorkbookPolicyPack(compiled_package),
            policy_context_builder=CompiledPolicyExecutionContextBuilder(compiled_package),
        )
        result = orchestrator.run(events)
    except Exception:
        knowledge_bundle = ensure_demo_knowledge_bundle(session)
        orchestrator = OutbreakOrchestrator(
            session=session,
            pathogen_pack=DemoInfluenzaPathogenPack(knowledge_bundle),
            policy_pack=DemoHospitalPolicyPack(knowledge_bundle),
        )
        result = orchestrator.run(events)
    return {
        "snapshot_at": result.snapshot_at,
        "assessment_count": len(result.assessments),
        "alert_count": len(result.alerts),
        "action_count": len(result.actions),
        "runtime_mode": result.runtime_mode,
        "knowledge_bundle_id": result.knowledge_bundle_id,
        "deployment_profile_id": result.deployment_profile_id,
        "matched_trigger_count": result.matched_trigger_count,
    }
