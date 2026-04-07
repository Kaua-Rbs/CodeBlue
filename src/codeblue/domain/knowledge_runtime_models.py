from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import Field

from codeblue.domain.canonical_events import EventEnvelope
from codeblue.domain.governance_models import TargetScope
from codeblue.domain.knowledge_models import ActionDefinition, KnowledgeBundle, KnowledgeModel
from codeblue.domain.state_models import StateSnapshotRef


class DeploymentProfile(KnowledgeModel):
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


class PolicyTriggerDefinition(KnowledgeModel):
    trigger_id: str
    trigger_name: str
    trigger_type: str
    input_source: str | None = None
    logic_definition: str | None = None
    trigger_window: str | None = None
    priority: str | None = None
    primary_action_family: str | None = None
    secondary_action_family: str | None = None
    related_features: list[str] = Field(default_factory=list)
    rationale: str | None = None
    source_document_ids: list[str] = Field(default_factory=list)
    status: str | None = None
    trigger_fact_name: str | None = None


class PolicyActionDefinition(KnowledgeModel):
    action_id: str
    action_name: str
    action_domain: str
    action_intent: str
    target_entity: str
    source_target_scope: str
    normalized_target_scope: TargetScope
    default_timing: str | None = None
    default_owner: str | None = None
    human_review_role: str | None = None
    review_requirement: str | None = None
    reversibility: str | None = None
    action_description: str | None = None
    direct_required_inputs: list[str] = Field(default_factory=list)
    contextual_inputs: list[str] = Field(default_factory=list)
    contraindications_or_blockers: list[str] = Field(default_factory=list)
    can_be_combined_with: list[str] = Field(default_factory=list)
    feasibility_notes: str | None = None
    audit_notes: str | None = None
    data_status: str | None = None
    source_document_ids: list[str] = Field(default_factory=list)

    def as_bundle_action_definition(self) -> ActionDefinition:
        reviewer_role = self.human_review_role or self.default_owner or "review_team"
        return ActionDefinition(
            action_id=self.action_id,
            display_name=self.action_name,
            category=self.action_domain,
            subtype=self.action_intent,
            description=self.action_description or self.action_name,
            pathogen_specificity=["influenza"],
            requires_reviewer_role=reviewer_role,
            target_scope=self.normalized_target_scope,
            must_be_logged=bool(self.audit_notes),
        )


class ContextModifierSet(KnowledgeModel):
    matched_contextual_inputs: list[str] = Field(default_factory=list)
    seasonality_modifier: str | None = None
    vaccination_modifier: str | None = None
    vulnerability_modifier: str | None = None
    spread_state_modifier: str | None = None
    capacity_modifier: str | None = None
    suppression_logic: str | None = None


class TriggerActionMapping(KnowledgeModel):
    map_id: str
    trigger_id: str
    action_id: str
    relationship_type: str
    timing_expectation: str | None = None
    base_priority: str | None = None
    activation_logic: str | None = None
    eligibility_logic: str | None = None
    modifiers: ContextModifierSet = Field(default_factory=ContextModifierSet)
    fallback_action_id: str | None = None
    review_role: str | None = None
    review_rationale: str | None = None
    data_status: str | None = None


class CompiledKnowledgePackage(KnowledgeModel):
    compiled_at: datetime = Field(default_factory=datetime.utcnow)
    source_directory: str
    knowledge_bundle: KnowledgeBundle
    deployment_profiles: list[DeploymentProfile] = Field(default_factory=list)
    policy_triggers: list[PolicyTriggerDefinition] = Field(default_factory=list)
    policy_action_catalog: list[PolicyActionDefinition] = Field(default_factory=list)
    trigger_action_mappings: list[TriggerActionMapping] = Field(default_factory=list)
    compiler_notes: list[str] = Field(default_factory=list)


class TriggerMatch(KnowledgeModel):
    trigger_id: str
    trigger_name: str
    fact_name: str
    target_scope: str
    target_id: str
    facts_used: dict[str, Any] = Field(default_factory=dict)


class PolicyExecutionContext(KnowledgeModel):
    runtime_mode: str = "legacy"
    events: list[EventEnvelope]
    snapshot: StateSnapshotRef
    hospital_id: str
    compiled_package: CompiledKnowledgePackage | None = None
    deployment_profile: DeploymentProfile | None = None
    runtime_facts: dict[str, Any] = Field(default_factory=dict)
    matched_triggers: list[TriggerMatch] = Field(default_factory=list)
    action_trace_index: dict[str, dict[str, Any]] = Field(default_factory=dict)
