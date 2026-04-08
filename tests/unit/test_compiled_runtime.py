from __future__ import annotations

from datetime import date
from pathlib import Path

from tests.fixtures.demo_events import build_demo_events

from codeblue.application.state_rebuilder import TemporalStateRebuilder
from codeblue.services.deployment_profile_service import DeploymentProfileService
from codeblue.services.knowledge_source_compiler import compile_workbook_source_package
from codeblue.services.policy_execution_context_builder import CompiledPolicyExecutionContextBuilder
from codeblue.services.policy_trigger_engine import PolicyTriggerEngine
from codeblue.services.trigger_action_mapper import TriggerActionMapper


def test_deployment_profile_service_resolves_windows() -> None:
    compiled = compile_workbook_source_package(Path("workbook"))
    service = DeploymentProfileService()
    profile = service.select_profile(compiled.deployment_profiles, "hospital_ce_001")

    assert profile is not None
    assert profile.seasonality_profile_id == "ceara_default_v1"
    assert (
        service.seasonality_flags(profile, date(2026, 2, 10))["seasonality.prealert_active"] is True
    )
    assert (
        service.seasonality_flags(profile, date(2026, 4, 7))["seasonality.high_alert_active"]
        is True
    )
    flags = service.seasonality_flags(profile, date(2026, 8, 1))
    assert flags["seasonality.prealert_active"] is False
    assert flags["seasonality.high_alert_active"] is False


def test_runtime_facts_builder_detects_supported_demo_facts() -> None:
    compiled = compile_workbook_source_package(Path("workbook"))
    events = build_demo_events()
    snapshot = TemporalStateRebuilder().rebuild_snapshot(
        events,
        max(event.occurred_at for event in events),
    )
    context = CompiledPolicyExecutionContextBuilder(compiled).build(events, snapshot)

    assert context.runtime_facts["seasonality.high_alert_active"]["matched"] is True
    assert "patient-2" in context.runtime_facts["symptoms.present_at_arrival"]
    assert "patient-1" in context.runtime_facts["case.suspected_or_confirmed_influenza"]
    assert "ward-a" in context.runtime_facts["ward.cluster_signal"]


def test_policy_trigger_engine_executes_only_supported_triggers() -> None:
    compiled = compile_workbook_source_package(Path("workbook"))
    events = build_demo_events()
    snapshot = TemporalStateRebuilder().rebuild_snapshot(
        events,
        max(event.occurred_at for event in events),
    )
    context = CompiledPolicyExecutionContextBuilder(compiled).build(events, snapshot)

    matches = PolicyTriggerEngine().evaluate(compiled.policy_triggers, context)

    assert len(matches) == 5
    assert {match.trigger_id for match in matches} == {
        "deployment_high_alert_window_active",
        "respiratory_symptoms_at_arrival",
        "suspected_or_confirmed_inpatient_influenza",
        "ward_cluster_signal",
    }


def test_trigger_action_mapper_resolves_targets_and_deduplicates() -> None:
    compiled = compile_workbook_source_package(Path("workbook"))
    events = build_demo_events()
    snapshot = TemporalStateRebuilder().rebuild_snapshot(
        events,
        max(event.occurred_at for event in events),
    )
    context = CompiledPolicyExecutionContextBuilder(compiled).build(events, snapshot)
    matches = PolicyTriggerEngine().evaluate(compiled.policy_triggers, context)
    trigger_index = {trigger.trigger_id: trigger for trigger in compiled.policy_triggers}
    action_index = {action.action_id: action for action in compiled.policy_action_catalog}

    actions = TriggerActionMapper().map_actions(
        trigger_matches=matches,
        trigger_index=trigger_index,
        action_index=action_index,
        mappings=compiled.trigger_action_mappings,
        context=context,
    )

    keys = {
        (action.action_definition_id, action.target_scope, action.target_id) for action in actions
    }
    assert len(keys) == len(actions)
    assert (
        "activate_screening_triage_and_visual_alerts",
        "entry_point",
        "hospital_ce_001:entry-point",
    ) in keys
    assert ("screen_and_mask_symptomatic_person", "patient", "patient-2") in keys
    assert ("implement_droplet_precautions_review", "room", "room-101") in keys
    assert ("staff_masking_escalation_review", "ward", "ward-a") in keys
    assert any(action.priority == "critical" for action in actions)
