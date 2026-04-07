from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

import pytest

openpyxl = pytest.importorskip("openpyxl")
Workbook = openpyxl.Workbook

from codeblue.domain.knowledge_ingestion_models import (
    KnowledgeSourceRole,
    KnowledgeSourceSchemaFamily,
)
from codeblue.services.knowledge_ingestion import (
    classify_knowledge_source_schema_family,
    classify_knowledge_source_sheet,
    infer_knowledge_table_schema_family,
    load_knowledge_source_csv_package,
    normalize_knowledge_header,
    parse_knowledge_source_workbook,
)


def test_classify_source_sheet_role_uses_live_tab_names() -> None:
    assert classify_knowledge_source_sheet("Riscos.2") == KnowledgeSourceRole.OVERVIEW_SYNTHESIS
    assert classify_knowledge_source_sheet("ha_influenza_risk_factors") == (
        KnowledgeSourceRole.CORE_EVIDENCE
    )
    assert classify_knowledge_source_sheet("staff_vector_transmission") == (
        KnowledgeSourceRole.COMPANION_EVIDENCE
    )
    assert classify_knowledge_source_sheet("library") == KnowledgeSourceRole.REFERENCE
    assert classify_knowledge_source_sheet("Pathogen info") == KnowledgeSourceRole.PLACEHOLDER


def test_classify_source_schema_family_matches_dictionary_expectations() -> None:
    assert classify_knowledge_source_schema_family("ha_influenza_risk_factors") == (
        KnowledgeSourceSchemaFamily.COMPACT_CORE
    )
    assert classify_knowledge_source_schema_family("transmission_context_support") == (
        KnowledgeSourceSchemaFamily.REFERENCE
    )
    assert classify_knowledge_source_schema_family("hospitalized_influenza_severity") == (
        KnowledgeSourceSchemaFamily.LEGACY_EXTENDED
    )
    assert classify_knowledge_source_schema_family("Riscos.2") == (
        KnowledgeSourceSchemaFamily.SYNTHESIS
    )


def test_normalize_header_handles_source_table_labels() -> None:
    assert normalize_knowledge_header("Hospital-acquired definition") == (
        "hospital_acquired_definition"
    )
    assert normalize_knowledge_header("PMID / DOI") == "pmid_doi"
    assert normalize_knowledge_header("Study-reported implication") == "study_reported_implication"


def test_infer_source_schema_family_from_headers() -> None:
    compact = ["source_id"] * 0 + [
        "source_id",
        "citation",
        "pathogen_scope",
        "canonical_feature_name",
        "codeblue_translation",
    ] + [f"extra_{idx}" for idx in range(28)]
    extended = compact + ["tags", "factor_role", "data_status"]
    legacy = extended + ["risk_factor_name"]

    assert infer_knowledge_table_schema_family(compact) == KnowledgeSourceSchemaFamily.COMPACT_CORE
    assert infer_knowledge_table_schema_family(extended) == KnowledgeSourceSchemaFamily.EXTENDED
    assert infer_knowledge_table_schema_family(legacy) == (
        KnowledgeSourceSchemaFamily.LEGACY_EXTENDED
    )


def test_parse_knowledge_source_workbook_skips_title_rows_and_duplicate_headers() -> None:
    workbook = Workbook()
    synthesis_sheet = workbook.active
    synthesis_sheet.title = "Riscos.2"
    synthesis_sheet.append(["Manual synthesis sheet"])
    synthesis_sheet.append(
        ["citation", "pathogen scope", "influenza-specific findings", "codeblue translation"]
    )
    synthesis_sheet.append(
        [
            "Example et al. 2025",
            "influenza and RSV",
            "Shared ward burden",
            "Use as synthesis only",
        ]
    )

    risk_sheet = workbook.create_sheet("ha_influenza_risk_factors")
    risk_sheet.title = "ha_influenza_risk_factors"
    risk_sheet.append(["Main acquisition table"])
    headers = [
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
    ]
    risk_sheet.append(headers)
    risk_sheet.append(headers)
    risk_sheet.append(
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
        ]
    )

    library_sheet = workbook.create_sheet("library")
    library_sheet.append(["Feature library"])
    library_sheet.append(
        [
            "canonical_feature_name",
            "alias_name",
            "feature_class",
            "default_temporal_stage",
            "description",
            "typical_effect_direction",
            "deployment_priority",
        ]
    )
    library_sheet.append(
        [
            "room_sharing",
            "double room",
            "structural",
            "during_exposure_window",
            "Shared room occupancy",
            "increase_risk",
            "core",
        ]
    )

    trigger_sheet = workbook.create_sheet("survaillence info - triggers")
    trigger_sheet.append(["Positive PCR after 48h"])
    trigger_sheet.append(["Clustered cases on the same ward"])

    abbr_sheet = workbook.create_sheet("abreviações")
    abbr_sheet.append(["Abbreviation", "Meaning"])
    abbr_sheet.append(["HA", "Hospital-Acquired"])

    workbook.create_sheet("Pathogen info").append(["reserved"])

    imported = parse_knowledge_source_workbook(workbook)

    risk_summary = next(
        sheet for sheet in imported.sheets if sheet.sheet_name == "ha_influenza_risk_factors"
    )
    synthesis_summary = next(sheet for sheet in imported.sheets if sheet.sheet_name == "Riscos.2")
    assert synthesis_summary.schema_family == KnowledgeSourceSchemaFamily.SYNTHESIS
    assert imported.synthesis_rows[0].row_payload["citation"] == "Example et al. 2025"
    assert risk_summary.skipped_title_rows == 1
    assert risk_summary.skipped_duplicate_header_rows == 1
    assert risk_summary.data_row_count == 1
    assert imported.evidence_rows[0].canonical_feature_name == "room_sharing"
    assert imported.library_entries[0].canonical_feature_name == "room_sharing"
    assert imported.trigger_entries[0].trigger_text == "Positive PCR after 48h"
    assert imported.abbreviation_entries[0].abbreviation == "HA"


def test_load_knowledge_source_csv_package_parses_structured_and_supporting_tables(
    tmp_path: Path,
) -> None:
    csv_dir = tmp_path

    def write_csv(name: str, rows: list[list[str]]) -> None:
        with (csv_dir / name).open("w", newline="", encoding="utf-8") as handle:
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
                "Symptoms usually begin about 2 days after infection",
                "Use a short default lookback window",
                "Strong CDC support",
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
            ["", "", "", "", "", "", "", "", "", "", "", "", "", ""],
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
                "None",
                "Escalate for vulnerable destinations",
                "Escalate if recent cases are rising",
                "Defer if mask supply is critically constrained",
                "Suppress only if already performed",
                "blank",
                "frontline_clinician_or_unit_lead",
                "Source-control should happen at first contact",
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
        "HSIL - abreviações.csv",
        [
            ["Abbreviations"],
            [],
            ["AOR — Adjusted Odds Ratio"],
            ["IPC — Infection Prevention and Control"],
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
    write_csv(
        "HSIL - unknown_future_table.csv",
        [["foo", "bar"], ["one", "two"]],
    )

    imported = load_knowledge_source_csv_package(csv_dir)

    assert imported.influenza_pack_timing_rows[0].timing_parameter == "incubation_period_usual"
    assert imported.deployment_profiles[0].manual_override_allowed is True
    assert imported.deployment_profiles[0].vaccination_campaign_start == date(2026, 3, 28)
    assert imported.policy_triggers[0].primary_action_family == "screen_and_mask_symptomatic_person"
    assert imported.action_library_rows[0].action_id == "screen_and_mask_symptomatic_person"
    assert imported.trigger_action_map_rows[0].fallback_action_id is None
    assert imported.library_entries[0].canonical_feature_name == "waiting_area_density"
    assert imported.abbreviation_entries[0].abbreviation == "AOR"
    assert imported.evidence_rows[0].canonical_feature_name == "room_sharing"
    assert "HSIL - unknown_future_table.csv" in imported.unmodeled_files

    trigger_summary = next(table for table in imported.tables if table.table_name == "policy_trigger_library")
    evidence_summary = next(table for table in imported.tables if table.table_name == "ha_influenza_risk_factors")
    assert trigger_summary.row_count == 1
    assert evidence_summary.skipped_title_rows == 1
