from __future__ import annotations

from tests.fixtures.demo_events import build_demo_events

from codeblue.api.routes.actions import list_actions
from codeblue.api.routes.events import ingest_events
from codeblue.api.routes.explainability import explain_action
from codeblue.api.routes.runs import trigger_run
from codeblue.api.schemas.events import IngestEventsRequest
from codeblue.persistence.db import SessionLocal, engine
from codeblue.persistence.orm_models import AuditRecordORM, Base


def test_compiled_runtime_pipeline_creates_actions_and_trace() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    events = [event.model_dump(mode="json") for event in build_demo_events()]

    with SessionLocal() as session:
        ingest_response = ingest_events(IngestEventsRequest(events=events), session)
        assert ingest_response.ingested_count == len(events)

        payload = trigger_run(session)
    assert payload["runtime_mode"] == "compiled"
    assert payload["knowledge_bundle_id"] == "kb_influenza_workbook_compiled_v1"
    assert payload["deployment_profile_id"] == "ceara_default_v1"
    assert payload["matched_trigger_count"] == 5
    assert payload["action_count"] >= 10

    with SessionLocal() as session:
        actions = [action.model_dump(mode="json") for action in list_actions(session)]
    action_definition_ids = {action["action_definition_id"] for action in actions}
    assert "activate_screening_triage_and_visual_alerts" in action_definition_ids
    assert "screen_and_mask_symptomatic_person" in action_definition_ids
    assert "implement_droplet_precautions_review" in action_definition_ids
    assert "staff_masking_escalation_review" in action_definition_ids

    top_action = next(
        action
        for action in actions
        if action["action_definition_id"] == "implement_droplet_precautions_review"
    )
    assert top_action["priority"] == "critical"
    assert "suspected_or_confirmed_inpatient_influenza" in top_action["triggering_rule_ids"]
    assert "audit_mode:must_log" in top_action["constraints_applied"]

    with SessionLocal() as session:
        explain_payload = explain_action(top_action["action_id"], session)
    assert explain_payload["trace"]["runtime_mode"] == "compiled"
    assert (
        "suspected_or_confirmed_inpatient_influenza"
        in explain_payload["trace"]["matched_trigger_ids"]
    )

    with SessionLocal() as session:
        audit_record = (
            session.query(AuditRecordORM).filter_by(entity_id=top_action["target_id"]).first()
        )
        assert audit_record is not None
        assert audit_record.details["runtime_mode"] == "compiled"
        assert audit_record.details["trace"]["matched_mapping_ids"]


def test_runs_route_falls_back_to_legacy_runtime_when_compiled_loader_fails(monkeypatch) -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    events = [event.model_dump(mode="json") for event in build_demo_events()]

    def raise_loader_error() -> None:
        raise RuntimeError("compiled runtime unavailable")

    monkeypatch.setattr(
        "codeblue.api.routes.runs.load_compiled_runtime_package_cached",
        raise_loader_error,
    )

    with SessionLocal() as session:
        ingest_response = ingest_events(IngestEventsRequest(events=events), session)
        assert ingest_response.ingested_count == len(events)
        payload = trigger_run(session)
    assert payload["runtime_mode"] == "legacy"
    assert payload["knowledge_bundle_id"] == "kb_codeblue_demo_v1"
    assert payload["matched_trigger_count"] == 0
    assert payload["action_count"] >= 1
