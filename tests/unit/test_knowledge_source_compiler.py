from __future__ import annotations

import csv
from pathlib import Path

from codeblue.services.knowledge_ingestion import load_knowledge_source_csv_package
from codeblue.services.knowledge_source_compiler import (
    compile_knowledge_source_package,
    compile_workbook_source_package,
)


def test_compile_knowledge_source_package_builds_runtime_artifacts(tmp_path: Path) -> None:
    def write_csv(name: str, rows: list[list[str]]) -> None:
        with (tmp_path / name).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerows(rows)

    write_csv(
        "HSIL - influenza_pack_timing.csv",
        [
            [
                "pack_id",
                "timing_parameter",
                "parameter_group",
                "default_value",
                "value_range",
                "unit",
                "applies_to",
                "modifier",
                "source_basis",
                "finding_text",
                "codeblue_translation",
                "confidence_note",
                "data_status",
            ],
            [
                "influenza_hai_v1",
                "incubation_period_usual",
                "biologic_timing",
                "2",
                "1-4",
                "days",
                "exposed_person",
                "usual seasonal influenza timing",
                "CDC Flu Spread 2024",
                "Symptoms typically begin about 2 days after infection",
                "Use a short lookback window",
                "Strong CDC support",
                "ready",
            ],
        ],
    )
    write_csv(
        "HSIL - influenza_pack_risk_features.csv",
        [
            [
                "pack_id",
                "canonical_feature_name",
                "priority_tier",
                "default_use_stage",
                "factor_role",
                "feature_class",
                "pathogen_relevance",
                "source_basis",
                "finding_text",
                "codeblue_translation",
                "caution_note",
                "data_status",
            ],
            [
                "influenza_hai_v1",
                "patient_annual_influenza_vaccination",
                "very_high",
                "admission_and_prevention",
                "protective",
                "vaccination",
                "Direct protective factor",
                "CDC Flu Infection Control 2025",
                "Annual influenza vaccination is the most important preventive measure",
                "Treat vaccination as a top protective feature",
                "Protective status does not rule out influenza",
                "ready",
            ],
        ],
    )
    write_csv(
        "HSIL - influenza_pack_interventions.csv",
        [
            [
                "pack_id",
                "intervention_name",
                "trigger_context",
                "target_entity",
                "timing_window",
                "action_type",
                "default_review_level",
                "operational_constraints",
                "source_basis",
                "finding_text",
                "codeblue_translation",
                "data_status",
            ],
            [
                "influenza_hai_v1",
                "screen_mask_and_respiratory_hygiene_review",
                "symptomatic_arrival_or_symptomatic_visitor",
                "patient_or_visitor",
                "immediate",
                "source_control_review",
                "frontline_team",
                "Requires mask supply",
                "CDC Flu Infection Control 2025",
                "Screening and respiratory hygiene are recommended",
                "Route source-control review at first contact",
                "ready",
            ],
        ],
    )
    write_csv(
        "HSIL - deployment_seasonality_profile.csv",
        [
            [
                "seasonality_profile_id",
                "hospital_id",
                "geography_label",
                "profile_status",
                "pre_alert_start_month",
                "high_alert_start_month",
                "high_alert_end_month",
                "deescalation_month",
                "year_round_background_risk",
                "vaccination_campaign_start",
                "vaccination_campaign_end",
                "community_activity_input_mode",
                "manual_override_allowed",
                "notes",
                "data_status",
            ],
            [
                "ceara_default_v1",
                "hospital_ce_001",
                "Ceara, Brazil",
                "active",
                "February",
                "March",
                "June",
                "July",
                "TRUE",
                "2026-03-28",
                "2026-05-30",
                "manual_plus_surveillance",
                "TRUE",
                "Editable by hospital",
                "required",
            ],
        ],
    )
    write_csv(
        "HSIL - policy_source_library.csv",
        [
            [
                "policy_source_id",
                "source_title",
                "issuing_body",
                "source_scope",
                "source_type",
                "last_update_or_publication",
                "primary_use_in_codeblue",
                "authority_notes",
                "data_status",
            ],
            [
                "cdc_flu_healthcare_settings_2025",
                "Infection Prevention and Control Strategies for Seasonal Influenza in Healthcare Settings",
                "CDC",
                "Influenza-specific healthcare infection control",
                "influenza_specific_policy_guidance",
                "2025-04-28",
                "Primary operational source for influenza triggers and actions",
                "Main influenza-control authority",
                "ready",
            ],
            [
                "cdc_flu_spread_2024",
                "How Flu Spreads",
                "CDC",
                "Influenza timing and contagiousness biology",
                "influenza_biology_guidance",
                "2024-09-17",
                "Primary source for incubation and contagious window",
                "Use in pack timing",
                "ready",
            ],
        ],
    )
    write_csv(
        "HSIL - policy_trigger_library.csv",
        [
            [
                "trigger_id",
                "trigger_name",
                "trigger_type",
                "input_source",
                "logic_definition",
                "trigger_window",
                "priority",
                "",
                "primary_action_family",
                "secondary_action_family",
                "related_features",
                "rationale",
                "recommended_source_basis",
                "status",
            ],
            [
                "respiratory_symptoms_at_arrival",
                "Respiratory symptoms at arrival",
                "symptom_entry_trigger",
                "registration_triage",
                "Arrival reports compatible respiratory symptoms",
                "Immediate / current shift",
                "high",
                "",
                "screen_and_mask_symptomatic_person",
                "rapid_influenza_test_review",
                "symptom_presence; arrival_location",
                "Should act before waiting-area exposure expands",
                "CDC Flu Infection Control 2025",
                "ready",
            ],
            [
                "deployment_prealert_window_active",
                "Deployment pre-alert window active",
                "deployment_trigger",
                "deployment_profile",
                "Current date enters the local pre-alert window",
                "Current period",
                "medium",
                "",
                "activate_screening_triage_and_visual_alerts",
                "",
                "seasonality_profile_id; current_date",
                "Should act before seasonal rise",
                "CDC Flu Infection Control 2025",
                "ready",
            ],
        ],
    )
    write_csv(
        "HSIL - action_library.csv",
        [
            [
                "action_id",
                "action_name",
                "action_domain",
                "action_intent",
                "target_entity",
                "target_scope",
                "default_timing",
                "default_owner",
                "human_review_role",
                "review_requirement",
                "reversibility",
                "action_description",
                "direct_required_inputs",
                "contextual_inputs",
                "contraindications_or_blockers",
                "can_be_combined_with",
                "feasibility_notes",
                "audit_notes",
                "data_status",
            ],
            [
                "screen_and_mask_symptomatic_person",
                "Screen and mask symptomatic person",
                "screening_and_source_control",
                "source_control",
                "patient_or_visitor",
                "individual",
                "at_first_contact",
                "frontline_team",
                "frontline_clinician_or_unit_lead",
                "required",
                "reversible",
                "Provide mask and route through triage",
                "symptoms; arrival_location; mask_availability",
                "seasonality_profile_id; waiting_area_density",
                "mask intolerance",
                "rapid_influenza_test_review",
                "Low-complexity action",
                "Log time and actor",
                "ready",
            ],
            [
                "activate_screening_triage_and_visual_alerts",
                "Activate screening, triage, and visual alerts",
                "screening_and_source_control",
                "front_end_source_control",
                "facility_or_unit",
                "entry_points_waiting_areas_and_registration",
                "preseason_or_when_activity_rises",
                "clinical_operations_plus_ipc",
                "unit_lead_or_ipc",
                "required",
                "reversible",
                "Activate front-end respiratory screening and alerts",
                "signage_availability; mask_supply",
                "seasonality_profile_id; current_date",
                "severe staffing shortage",
                "screen_and_mask_symptomatic_person",
                "Mostly operational",
                "Log activation date",
                "ready",
            ],
        ],
    )
    write_csv(
        "HSIL - trigger_action_map.csv",
        [
            [
                "map_id",
                "trigger_id",
                "action_id",
                "relationship_type",
                "timing_expectation",
                "base_priority",
                "activation_logic",
                "eligibility_logic",
                "matched_contextual_inputs",
                "seasonality_modifier",
                "vaccination_modifier",
                "vulnerability_modifier",
                "spread_state_modifier",
                "capacity_modifier",
                "suppression_logic",
                "fallback_action_id",
                "review_role",
                "review_rationale",
                "data_status",
            ],
            [
                "map_001",
                "respiratory_symptoms_at_arrival",
                "screen_and_mask_symptomatic_person",
                "recommended",
                "immediate",
                "high",
                "Always when symptoms are present at arrival",
                "Applies at intake",
                "seasonality_profile_id; waiting_area_density",
                "Escalate during high-alert window",
                "",
                "Escalate for vulnerable destinations",
                "",
                "Defer if mask supply is critically constrained",
                "Suppress only if already performed",
                "blank",
                "frontline_clinician_or_unit_lead",
                "Source-control should happen at first contact",
                "ready",
            ],
            [
                "map_002",
                "deployment_prealert_window_active",
                "activate_screening_triage_and_visual_alerts",
                "recommended",
                "prealert_window",
                "medium",
                "Activate when local pre-alert period begins",
                "Applies to intake workflows",
                "seasonality_profile_id; current_date",
                "Increase preparedness before local rise",
                "",
                "Escalate in facilities serving vulnerable populations",
                "",
                "Minimal capacity effect",
                "Suppress if already active",
                "blank",
                "unit_lead_or_ipc",
                "Pre-alert should move before the seasonal peak",
                "ready",
            ],
        ],
    )
    write_csv(
        "HSIL - library.csv",
        [
            [
                "canonical_feature_name",
                "alias_name",
                "feature_class",
                "default_temporal_stage",
                "description",
                "typical_effect_direction",
                "deployment_priority",
            ],
            [
                "waiting_area_density",
                "crowded waiting area",
                "operational",
                "arrival",
                "Waiting area crowding",
                "increase_risk",
                "high",
            ],
        ],
    )
    write_csv(
        "HSIL - ha_influenza_risk_factors.csv",
        [
            ["Main acquisition table"],
            [
                "source_id",
                "citation",
                "pmid",
                "doi",
                "country",
                "setting",
                "population",
                "study_design",
                "pathogen_scope",
                "acquisition_context",
                "hospital_acquired_definition",
                "diagnostic_method",
                "surveillance_frame",
                "comparator_group",
                "canonical_feature_name",
                "risk_factor_type",
                "feature_class",
                "temporal_stage",
                "risk_factor_definition",
                "finding_text",
                "effect_size",
                "effect_size_type",
                "confidence_interval",
                "p_value",
                "effect_direction",
                "evidence_strength",
                "adjustment_level",
                "outcome_linked",
                "clinical_context",
                "applicability_to_influenza",
                "key_limitations",
                "study_reported_implication",
                "codeblue_translation",
            ],
            [
                "zhang_2025",
                "Zhang et al. 2025",
                "123456",
                "10.1000/example",
                "China",
                "Tertiary hospital",
                "Adults",
                "Cohort",
                "influenza_only",
                "hospital_acquired",
                ">48h",
                "PCR",
                "2019-2024",
                "HA vs CA",
                "room_sharing",
                "clinical_association",
                "structural",
                "during_exposure_window",
                "Shared room",
                "Associated with HA influenza",
                "3.1",
                "OR",
                "1.2-7.8",
                "0.01",
                "increase_risk",
                "moderate",
                "multivariable",
                "acquisition",
                "Adult ward",
                "influenza_only",
                "Single center",
                "Room sharing increased transmission",
                "Add room occupancy feature",
            ],
        ],
    )

    package = load_knowledge_source_csv_package(tmp_path)
    compiled = compile_knowledge_source_package(package)

    assert compiled.knowledge_bundle.bundle_id == "kb_influenza_workbook_compiled_v1"
    assert len(compiled.deployment_profiles) == 1
    assert len(compiled.policy_triggers) == 2
    assert len(compiled.policy_action_catalog) == 2
    assert len(compiled.trigger_action_mappings) == 2

    action = next(
        item for item in compiled.policy_action_catalog if item.action_id == "activate_screening_triage_and_visual_alerts"
    )
    assert action.normalized_target_scope == "entry_point"

    trigger = next(
        item for item in compiled.policy_triggers if item.trigger_id == "deployment_prealert_window_active"
    )
    assert trigger.trigger_fact_name == "seasonality.prealert_active"
    assert trigger.source_document_ids == ["cdc_flu_healthcare_settings_2025"]

    assert any(rule.rule_id == "review_map_001" for rule in compiled.knowledge_bundle.rule_artifacts)
    assert any(rule.rule_id == "policy_audit_screen_and_mask_symptomatic_person" for rule in compiled.knowledge_bundle.rule_artifacts)
    assert any(
        case.test_case_id == "tc_compiled_respiratory_symptoms_at_arrival"
        for case in compiled.knowledge_bundle.test_cases
    )
    assert any(
        document.source_document_id == "zhang_2025"
        for document in compiled.knowledge_bundle.source_documents
    )
    assert any(
        statement.evidence_statement_id.startswith("evidence_lit_")
        for statement in compiled.knowledge_bundle.evidence_statements
    )


def test_compile_workbook_source_package_smoke_uses_real_workbook() -> None:
    compiled = compile_workbook_source_package(Path("workbook"))

    assert len(compiled.deployment_profiles) == 1
    assert len(compiled.policy_triggers) == 21
    assert len(compiled.policy_action_catalog) == 19
    assert len(compiled.trigger_action_mappings) == 34
    assert len(compiled.knowledge_bundle.action_catalog) == 19
    assert len(compiled.knowledge_bundle.rule_artifacts) >= 34
