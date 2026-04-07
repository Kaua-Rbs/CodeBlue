from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum

from pydantic import Field, field_validator

from codeblue.domain.knowledge_models import KnowledgeModel


class KnowledgeSourceSchemaFamily(StrEnum):
    COMPACT_CORE = "compact_core"
    EXTENDED = "extended"
    LEGACY_EXTENDED = "legacy_extended"
    REFERENCE = "reference"
    SYNTHESIS = "synthesis"
    PLACEHOLDER = "placeholder"


class KnowledgeSourceRole(StrEnum):
    CORE_EVIDENCE = "core_evidence"
    COMPANION_EVIDENCE = "companion_evidence"
    REFERENCE = "reference"
    OVERVIEW_SYNTHESIS = "overview_synthesis"
    PLACEHOLDER = "placeholder"


class KnowledgeSheetSummary(KnowledgeModel):
    sheet_name: str
    role: KnowledgeSourceRole
    schema_family: KnowledgeSourceSchemaFamily
    header_row_index: int | None = None
    skipped_title_rows: int = 0
    skipped_duplicate_header_rows: int = 0
    data_row_count: int = 0


class KnowledgeEvidenceRow(KnowledgeModel):
    sheet_name: str
    schema_family: KnowledgeSourceSchemaFamily
    source_id: str | None = None
    citation: str | None = None
    pmid: str | None = None
    doi: str | None = None
    country: str | None = None
    setting: str | None = None
    population: str | None = None
    study_design: str | None = None
    pathogen_scope: str | None = None
    acquisition_context: str | None = None
    hospital_acquired_definition: str | None = None
    diagnostic_method: str | None = None
    surveillance_frame: str | None = None
    comparator_group: str | None = None
    canonical_feature_name: str | None = None
    risk_factor_type: str | None = None
    feature_class: str | None = None
    temporal_stage: str | None = None
    risk_factor_definition: str | None = None
    finding_text: str | None = None
    effect_size: str | None = None
    effect_size_type: str | None = None
    confidence_interval: str | None = None
    p_value: str | None = None
    effect_direction: str | None = None
    evidence_strength: str | None = None
    adjustment_level: str | None = None
    outcome_linked: str | None = None
    clinical_context: str | None = None
    applicability_to_influenza: str | None = None
    key_limitations: str | None = None
    study_reported_implication: str | None = None
    codeblue_translation: str | None = None
    tags: str | None = None
    factor_role: str | None = None
    data_status: str | None = None
    risk_factor_name: str | None = None


class KnowledgeLibraryEntry(KnowledgeModel):
    canonical_feature_name: str
    alias_name: str | None = None
    feature_class: str | None = None
    default_temporal_stage: str | None = None
    description: str | None = None
    typical_effect_direction: str | None = None
    deployment_priority: str | None = None


class KnowledgeTriggerEntry(KnowledgeModel):
    trigger_text: str


class KnowledgeAbbreviationEntry(KnowledgeModel):
    abbreviation: str
    meaning: str


class KnowledgeSynthesisRow(KnowledgeModel):
    sheet_name: str
    row_payload: dict[str, str] = Field(default_factory=dict)


class KnowledgeSourceImport(KnowledgeModel):
    source_name: str
    imported_at: datetime = Field(default_factory=datetime.utcnow)
    sheets: list[KnowledgeSheetSummary] = Field(default_factory=list)
    evidence_rows: list[KnowledgeEvidenceRow] = Field(default_factory=list)
    synthesis_rows: list[KnowledgeSynthesisRow] = Field(default_factory=list)
    library_entries: list[KnowledgeLibraryEntry] = Field(default_factory=list)
    trigger_entries: list[KnowledgeTriggerEntry] = Field(default_factory=list)
    abbreviation_entries: list[KnowledgeAbbreviationEntry] = Field(default_factory=list)


class KnowledgeCsvSourceRow(KnowledgeModel):
    @field_validator("*", mode="before")
    @classmethod
    def normalize_source_value(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip()
            if not normalized or normalized.lower() == "blank":
                return None
            return normalized
        return value


class KnowledgeCsvTableSummary(KnowledgeModel):
    file_name: str
    table_name: str
    handled_as: str
    row_count: int = 0
    header_row_index: int | None = None
    skipped_title_rows: int = 0
    skipped_duplicate_header_rows: int = 0


class InfluenzaPackTimingRow(KnowledgeCsvSourceRow):
    pack_id: str
    timing_parameter: str
    parameter_group: str
    default_value: str | None = None
    value_range: str | None = None
    unit: str | None = None
    applies_to: str | None = None
    modifier: str | None = None
    source_basis: str | None = None
    finding_text: str | None = None
    codeblue_translation: str | None = None
    confidence_note: str | None = None
    data_status: str | None = None


class InfluenzaPackRiskFeatureRow(KnowledgeCsvSourceRow):
    pack_id: str
    canonical_feature_name: str
    priority_tier: str
    default_use_stage: str
    factor_role: str | None = None
    feature_class: str | None = None
    pathogen_relevance: str | None = None
    source_basis: str | None = None
    finding_text: str | None = None
    codeblue_translation: str | None = None
    caution_note: str | None = None
    data_status: str | None = None


class InfluenzaPackInterventionRow(KnowledgeCsvSourceRow):
    pack_id: str
    intervention_name: str
    trigger_context: str | None = None
    target_entity: str | None = None
    timing_window: str | None = None
    action_type: str | None = None
    default_review_level: str | None = None
    operational_constraints: str | None = None
    source_basis: str | None = None
    finding_text: str | None = None
    codeblue_translation: str | None = None
    data_status: str | None = None


class DeploymentSeasonalityProfileRow(KnowledgeCsvSourceRow):
    seasonality_profile_id: str
    hospital_id: str
    geography_label: str
    profile_status: str
    pre_alert_start_month: str | None = None
    high_alert_start_month: str | None = None
    high_alert_end_month: str | None = None
    deescalation_month: str | None = None
    year_round_background_risk: bool | None = None
    vaccination_campaign_start: date | None = None
    vaccination_campaign_end: date | None = None
    community_activity_input_mode: str | None = None
    manual_override_allowed: bool | None = None
    notes: str | None = None
    data_status: str | None = None


class PolicySourceRow(KnowledgeCsvSourceRow):
    policy_source_id: str
    source_title: str
    issuing_body: str
    source_scope: str
    source_type: str
    last_update_or_publication: str | None = None
    primary_use_in_codeblue: str | None = None
    authority_notes: str | None = None
    data_status: str | None = None


class PolicyTriggerRow(KnowledgeCsvSourceRow):
    trigger_id: str
    trigger_name: str
    trigger_type: str
    input_source: str | None = None
    logic_definition: str | None = None
    trigger_window: str | None = None
    priority: str | None = None
    primary_action_family: str | None = None
    secondary_action_family: str | None = None
    related_features: str | None = None
    rationale: str | None = None
    recommended_source_basis: str | None = None
    status: str | None = None


class ActionLibraryRow(KnowledgeCsvSourceRow):
    action_id: str
    action_name: str
    action_domain: str
    action_intent: str
    target_entity: str
    target_scope: str
    default_timing: str | None = None
    default_owner: str | None = None
    human_review_role: str | None = None
    review_requirement: str | None = None
    reversibility: str | None = None
    action_description: str | None = None
    direct_required_inputs: str | None = None
    contextual_inputs: str | None = None
    contraindications_or_blockers: str | None = None
    can_be_combined_with: str | None = None
    feasibility_notes: str | None = None
    audit_notes: str | None = None
    data_status: str | None = None


class TriggerActionMapRow(KnowledgeCsvSourceRow):
    map_id: str
    trigger_id: str
    action_id: str
    relationship_type: str
    timing_expectation: str | None = None
    base_priority: str | None = None
    activation_logic: str | None = None
    eligibility_logic: str | None = None
    matched_contextual_inputs: str | None = None
    seasonality_modifier: str | None = None
    vaccination_modifier: str | None = None
    vulnerability_modifier: str | None = None
    spread_state_modifier: str | None = None
    capacity_modifier: str | None = None
    suppression_logic: str | None = None
    fallback_action_id: str | None = None
    review_role: str | None = None
    review_rationale: str | None = None
    data_status: str | None = None


class KnowledgeSourceCsvPackage(KnowledgeModel):
    source_directory: str
    imported_at: datetime = Field(default_factory=datetime.utcnow)
    tables: list[KnowledgeCsvTableSummary] = Field(default_factory=list)
    evidence_rows: list[KnowledgeEvidenceRow] = Field(default_factory=list)
    library_entries: list[KnowledgeLibraryEntry] = Field(default_factory=list)
    abbreviation_entries: list[KnowledgeAbbreviationEntry] = Field(default_factory=list)
    influenza_pack_timing_rows: list[InfluenzaPackTimingRow] = Field(default_factory=list)
    influenza_pack_risk_feature_rows: list[InfluenzaPackRiskFeatureRow] = Field(
        default_factory=list
    )
    influenza_pack_intervention_rows: list[InfluenzaPackInterventionRow] = Field(
        default_factory=list
    )
    deployment_profiles: list[DeploymentSeasonalityProfileRow] = Field(default_factory=list)
    policy_sources: list[PolicySourceRow] = Field(default_factory=list)
    policy_triggers: list[PolicyTriggerRow] = Field(default_factory=list)
    action_library_rows: list[ActionLibraryRow] = Field(default_factory=list)
    trigger_action_map_rows: list[TriggerActionMapRow] = Field(default_factory=list)
    unmodeled_files: list[str] = Field(default_factory=list)
