from __future__ import annotations

import re
from collections import defaultdict
from datetime import UTC, date, datetime
from pathlib import Path

from codeblue.domain.governance_models import ExecutionMode, TargetScope
from codeblue.domain.knowledge_ingestion_models import (
    ActionLibraryRow,
    InfluenzaPackInterventionRow,
    InfluenzaPackRiskFeatureRow,
    InfluenzaPackTimingRow,
    KnowledgeEvidenceRow,
    KnowledgeLibraryEntry,
    KnowledgeSourceCsvPackage,
    PolicySourceRow,
    PolicyTriggerRow,
    TriggerActionMapRow,
)
from codeblue.domain.knowledge_models import (
    BundleStatus,
    ConfidenceLevel,
    ConstraintOutput,
    EvidenceStatement,
    IngestionMode,
    KnowledgeBundle,
    KnowledgeTestCase,
    MachineReadability,
    PathogenPack,
    PolicyPack,
    ProposedActionOutput,
    ReviewWorkflowPack,
    RuleArtifact,
    RuleCondition,
    RuleKind,
    RuleOperator,
    SourceDocument,
    TerminologyBinding,
)
from codeblue.domain.knowledge_runtime_models import (
    CompiledKnowledgePackage,
    ContextModifierSet,
    DeploymentProfile,
    PolicyActionDefinition,
    PolicyTriggerDefinition,
    TriggerActionMapping,
)
from codeblue.services.knowledge_ingestion import load_knowledge_source_csv_package

DEFAULT_BUNDLE_ID = "kb_influenza_workbook_compiled_v1"
DEFAULT_POLICY_PACK_ID = "policy_influenza_operational_v1"
DEFAULT_WORKFLOW_PACK_ID = "workflow_influenza_operational_v1"

TRIGGER_FACTS_BY_ID = {
    "respiratory_symptoms_at_arrival": "symptoms.present_at_arrival",
    "suspected_or_confirmed_inpatient_influenza": "case.suspected_or_confirmed_influenza",
    "same_room_exposure_to_confirmed_case": "exposure.same_room_to_confirmed_case",
    "same_unit_exposure_to_confirmed_case": "exposure.same_unit_to_confirmed_case",
    "single_room_unavailable_for_influenza_case": (
        "capacity.single_room_unavailable_for_influenza_case"
    ),
    "ill_hcp_detected": "hcw.ill_detected",
    "hcp_returns_with_residual_respiratory_symptoms": (
        "hcw.returned_with_residual_respiratory_symptoms"
    ),
    "exposed_hcp_assigned_to_high_vulnerability_ward": (
        "hcw.exposed_assigned_high_vulnerability_ward"
    ),
    "ward_cluster_signal": "ward.cluster_signal",
    "patient_transport_under_precautions": "patient.transport_under_precautions",
    "visitor_request_while_patient_infectious": "visitor.request_while_patient_infectious",
    "planned_or_emergent_agp": "procedure.agp_planned_or_emergent",
    "treatment_or_prophylaxis_consideration": "treatment.prophylaxis_consideration",
    "persistent_symptoms_or_shedding_beyond_default_window": (
        "case.persistent_symptoms_or_shedding_beyond_default_window"
    ),
    "protective_environment_hcp_assignment": "assignment.protective_environment_hcp",
    "manual_clinician_or_ipc_override": "manual.clinician_or_ipc_override",
    "deployment_prealert_window_active": "seasonality.prealert_active",
    "deployment_high_alert_window_active": "seasonality.high_alert_active",
    "elevated_current_community_activity": "burden.elevated_current_community_activity",
    "elevated_current_hospital_burden": "burden.elevated_current_hospital_burden",
    "manual_epidemiology_override": "manual.epidemiology_override",
}

SOURCE_BASIS_ALIASES_BY_POLICY_SOURCE_ID = {
    "cdc_flu_healthcare_settings_2025": {
        "cdc flu infection control 2025",
        "cdc flu infection control",
    },
    "cdc_flu_antivirals_2026": {"cdc flu antivirals 2026", "cdc antivirals 2026"},
    "cdc_flu_spread_2024": {"cdc flu spread 2024", "cdc flu spread"},
    "cdc_flu_highrisk_2024": {"cdc high risk 2024", "cdc flu high risk 2024"},
    "cdc_core_practices_2024": {"cdc core practices 2024"},
    "cdc_isolation_precautions_2023": {"cdc isolation precautions 2023"},
    "br_ms_influenza_strategy_2026": {
        "ms influenza strategy 2026",
        "br ms influenza strategy 2026",
    },
    "ce_sesa_respiratory_seasonality_2026": {
        "ceara respiratory seasonality 2026",
        "ceara seasonality 2026",
    },
}


def compile_workbook_source_package(
    path: Path,
    *,
    bundle_id: str = DEFAULT_BUNDLE_ID,
) -> CompiledKnowledgePackage:
    package = load_knowledge_source_csv_package(path)
    return compile_knowledge_source_package(package, bundle_id=bundle_id)


def compile_knowledge_source_package(
    package: KnowledgeSourceCsvPackage,
    *,
    bundle_id: str = DEFAULT_BUNDLE_ID,
) -> CompiledKnowledgePackage:
    now = datetime.now(UTC)

    source_documents = compile_source_documents(package)
    source_document_ids = {document.source_document_id for document in source_documents}
    source_basis_lookup = build_source_basis_lookup(package.policy_sources)

    pathogen_pack_id = infer_pathogen_pack_id(package)
    policy_pack_id = DEFAULT_POLICY_PACK_ID
    workflow_pack_id = DEFAULT_WORKFLOW_PACK_ID

    policy_action_catalog = compile_policy_action_catalog(
        package.action_library_rows,
        source_basis_lookup=source_basis_lookup,
    )
    policy_action_index = {action.action_id: action for action in policy_action_catalog}
    deployment_profiles = compile_deployment_profiles(package)
    policy_triggers = compile_policy_triggers(package.policy_triggers, source_basis_lookup)
    trigger_index = {trigger.trigger_id: trigger for trigger in policy_triggers}
    trigger_action_mappings = compile_trigger_action_mappings(package.trigger_action_map_rows)
    terminology_bindings = compile_terminology_bindings(package.library_entries)

    evidence_statements = compile_evidence_statements(
        package=package,
        source_basis_lookup=source_basis_lookup,
        source_document_ids=source_document_ids,
    )
    rule_artifacts = compile_review_rules(
        trigger_action_mappings=trigger_action_mappings,
        trigger_index=trigger_index,
        action_index=policy_action_index,
        workflow_pack_id=workflow_pack_id,
    )
    rule_artifacts.extend(
        compile_policy_constraint_rules(
            policy_action_catalog=policy_action_catalog,
            policy_pack_id=policy_pack_id,
        )
    )
    test_cases = compile_bundle_test_cases(trigger_action_mappings, trigger_index)

    bundle = KnowledgeBundle(
        bundle_id=bundle_id,
        name="Compiled Influenza Workbook Knowledge Bundle",
        version="1.0.0",
        status=BundleStatus.DRAFT,
        created_at=now,
        updated_at=now,
        jurisdiction=infer_bundle_jurisdiction(package),
        organization="CodeBlue",
        description=(
            "Compiled influenza workbook bundle for the hackathon demo path, with "
            "deployment profile, policy triggers, action catalog, and review rules."
        ),
        source_documents=source_documents,
        terminology_bindings=terminology_bindings,
        pathogen_packs=[
            PathogenPack(
                pathogen_pack_id=pathogen_pack_id,
                pathogen_code="influenza",
                display_name="Influenza HAI",
                version="1.0.0",
                status=BundleStatus.DRAFT,
                source_document_ids=sorted(
                    set(
                        source_id
                        for row in package.influenza_pack_timing_rows
                        for source_id in resolve_source_basis_to_ids(
                            row.source_basis, source_basis_lookup
                        )
                    )
                ),
                notes="Compiled from influenza pack timing, risk-feature, and intervention tables.",
            )
        ],
        policy_packs=[
            PolicyPack(
                policy_pack_id=policy_pack_id,
                name="Influenza Operational Policy Pack",
                version="1.0.0",
                jurisdiction=infer_bundle_jurisdiction(package),
                organization="CodeBlue",
                source_document_ids=[
                    doc.source_document_id
                    for doc in source_documents
                    if doc.document_type != "study"
                ],
            )
        ],
        review_workflow_packs=[
            ReviewWorkflowPack(
                workflow_pack_id=workflow_pack_id,
                name="Influenza Operational Workflow Pack",
                version="1.0.0",
                source_document_ids=[
                    doc.source_document_id
                    for doc in source_documents
                    if doc.document_type != "study"
                ],
            )
        ],
        evidence_statements=evidence_statements,
        rule_artifacts=rule_artifacts,
        action_catalog=[action.as_bundle_action_definition() for action in policy_action_catalog],
        test_cases=test_cases,
    )

    compiler_notes = [
        "Compiled architecture-shaped influenza source tables into runtime deployment, "
        "trigger, action, and mapping objects.",
        "Generated review rules only for trigger ids that map cleanly to boolean runtime facts.",
        "Preserved detailed policy actions separately from the generic KnowledgeBundle "
        "action catalog.",
    ]

    return CompiledKnowledgePackage(
        source_directory=package.source_directory,
        knowledge_bundle=bundle,
        deployment_profiles=deployment_profiles,
        policy_triggers=policy_triggers,
        policy_action_catalog=policy_action_catalog,
        trigger_action_mappings=trigger_action_mappings,
        compiler_notes=compiler_notes,
    )


def infer_pathogen_pack_id(package: KnowledgeSourceCsvPackage) -> str:
    pack_ids = {
        row.pack_id
        for row in (
            package.influenza_pack_timing_rows
            + package.influenza_pack_risk_feature_rows
            + package.influenza_pack_intervention_rows
        )
        if row.pack_id
    }
    return sorted(pack_ids)[0] if pack_ids else "influenza_hai_v1"


def infer_bundle_jurisdiction(package: KnowledgeSourceCsvPackage) -> str:
    if any(
        profile.geography_label and "brazil" in profile.geography_label.lower()
        for profile in package.deployment_profiles
    ):
        return "Brazil"
    return "generic"


def compile_source_documents(package: KnowledgeSourceCsvPackage) -> list[SourceDocument]:
    documents: dict[str, SourceDocument] = {}

    for policy_source in package.policy_sources:
        publication_date = parse_full_date(policy_source.last_update_or_publication)
        documents[policy_source.policy_source_id] = SourceDocument(
            source_document_id=policy_source.policy_source_id,
            title=policy_source.source_title,
            organization=policy_source.issuing_body,
            document_type=normalize_document_type(policy_source.source_type),
            publication_date=publication_date,
            version_label=policy_source.last_update_or_publication,
            jurisdiction=infer_source_jurisdiction(policy_source),
            setting_scope=(
                ["hospital"] if "healthcare" in (policy_source.source_scope or "").lower() else []
            ),
            url=None,
            language="en",
            machine_readability=MachineReadability.PROSE,
            ingestion_mode=IngestionMode.TEMPLATE_IMPORT,
            notes=policy_source.primary_use_in_codeblue or policy_source.authority_notes,
        )

    for evidence_row in package.evidence_rows:
        if not evidence_row.source_id or evidence_row.source_id in documents:
            continue
        documents[evidence_row.source_id] = SourceDocument(
            source_document_id=evidence_row.source_id,
            title=evidence_row.citation or evidence_row.source_id,
            organization=evidence_row.country or "literature_source",
            document_type="study",
            publication_date=None,
            version_label=evidence_row.study_design,
            jurisdiction=evidence_row.country or "generic",
            setting_scope=[evidence_row.setting] if evidence_row.setting else [],
            url=build_doi_url(evidence_row.doi),
            language="en",
            machine_readability=MachineReadability.SEMI_STRUCTURED,
            ingestion_mode=IngestionMode.TEMPLATE_IMPORT,
            notes=evidence_row.key_limitations or evidence_row.study_reported_implication,
        )

    return sorted(documents.values(), key=lambda document: document.source_document_id)


def compile_deployment_profiles(
    package: KnowledgeSourceCsvPackage,
) -> list[DeploymentProfile]:
    return [
        DeploymentProfile(
            seasonality_profile_id=row.seasonality_profile_id,
            hospital_id=row.hospital_id,
            geography_label=row.geography_label,
            profile_status=row.profile_status,
            pre_alert_start_month=row.pre_alert_start_month,
            high_alert_start_month=row.high_alert_start_month,
            high_alert_end_month=row.high_alert_end_month,
            deescalation_month=row.deescalation_month,
            year_round_background_risk=row.year_round_background_risk,
            vaccination_campaign_start=row.vaccination_campaign_start,
            vaccination_campaign_end=row.vaccination_campaign_end,
            community_activity_input_mode=row.community_activity_input_mode,
            manual_override_allowed=row.manual_override_allowed,
            notes=row.notes,
            data_status=row.data_status,
        )
        for row in package.deployment_profiles
    ]


def compile_policy_triggers(
    rows: list[PolicyTriggerRow],
    source_basis_lookup: dict[str, str],
) -> list[PolicyTriggerDefinition]:
    compiled: list[PolicyTriggerDefinition] = []
    for row in rows:
        compiled.append(
            PolicyTriggerDefinition(
                trigger_id=row.trigger_id,
                trigger_name=row.trigger_name,
                trigger_type=row.trigger_type,
                input_source=row.input_source,
                logic_definition=row.logic_definition,
                trigger_window=row.trigger_window,
                priority=row.priority,
                primary_action_family=row.primary_action_family,
                secondary_action_family=row.secondary_action_family,
                related_features=split_multi_value(row.related_features),
                rationale=row.rationale,
                source_document_ids=resolve_source_basis_to_ids(
                    row.recommended_source_basis,
                    source_basis_lookup,
                ),
                status=row.status,
                trigger_fact_name=TRIGGER_FACTS_BY_ID.get(row.trigger_id),
            )
        )
    return compiled


def compile_policy_action_catalog(
    rows: list[ActionLibraryRow],
    *,
    source_basis_lookup: dict[str, str],
) -> list[PolicyActionDefinition]:
    return [
        PolicyActionDefinition(
            action_id=row.action_id,
            action_name=row.action_name,
            action_domain=row.action_domain,
            action_intent=row.action_intent,
            target_entity=row.target_entity,
            source_target_scope=row.target_scope,
            normalized_target_scope=normalize_action_target_scope(row),
            default_timing=row.default_timing,
            default_owner=row.default_owner,
            human_review_role=row.human_review_role,
            review_requirement=row.review_requirement,
            reversibility=row.reversibility,
            action_description=row.action_description,
            direct_required_inputs=split_multi_value(row.direct_required_inputs),
            contextual_inputs=split_multi_value(row.contextual_inputs),
            contraindications_or_blockers=split_multi_value(row.contraindications_or_blockers),
            can_be_combined_with=split_multi_value(row.can_be_combined_with),
            feasibility_notes=row.feasibility_notes,
            audit_notes=row.audit_notes,
            data_status=row.data_status,
            source_document_ids=resolve_source_basis_to_ids(None, source_basis_lookup),
        )
        for row in rows
    ]


def compile_trigger_action_mappings(
    rows: list[TriggerActionMapRow],
) -> list[TriggerActionMapping]:
    compiled: list[TriggerActionMapping] = []
    for row in rows:
        compiled.append(
            TriggerActionMapping(
                map_id=row.map_id,
                trigger_id=row.trigger_id,
                action_id=row.action_id,
                relationship_type=row.relationship_type,
                timing_expectation=row.timing_expectation,
                base_priority=row.base_priority,
                activation_logic=row.activation_logic,
                eligibility_logic=row.eligibility_logic,
                modifiers=ContextModifierSet(
                    matched_contextual_inputs=split_multi_value(row.matched_contextual_inputs),
                    seasonality_modifier=row.seasonality_modifier,
                    vaccination_modifier=row.vaccination_modifier,
                    vulnerability_modifier=row.vulnerability_modifier,
                    spread_state_modifier=row.spread_state_modifier,
                    capacity_modifier=row.capacity_modifier,
                    suppression_logic=row.suppression_logic,
                ),
                fallback_action_id=row.fallback_action_id,
                review_role=row.review_role,
                review_rationale=row.review_rationale,
                data_status=row.data_status,
            )
        )
    return compiled


def compile_terminology_bindings(
    rows: list[KnowledgeLibraryEntry],
) -> list[TerminologyBinding]:
    bindings: list[TerminologyBinding] = []
    for row in rows:
        if not row.alias_name:
            continue
        binding_id = normalize_identifier(f"binding_{row.canonical_feature_name}_{row.alias_name}")
        bindings.append(
            TerminologyBinding(
                binding_id=binding_id,
                local_system="knowledge_library",
                local_code=row.alias_name,
                local_display=row.alias_name,
                canonical_field="feature.name",
                canonical_value=row.canonical_feature_name,
            )
        )
    return bindings


def compile_evidence_statements(
    *,
    package: KnowledgeSourceCsvPackage,
    source_basis_lookup: dict[str, str],
    source_document_ids: set[str],
) -> list[EvidenceStatement]:
    statements: list[EvidenceStatement] = []
    statements.extend(
        compile_pack_timing_evidence(package.influenza_pack_timing_rows, source_basis_lookup)
    )
    statements.extend(
        compile_pack_risk_feature_evidence(
            package.influenza_pack_risk_feature_rows,
            source_basis_lookup,
        )
    )
    statements.extend(
        compile_pack_intervention_evidence(
            package.influenza_pack_intervention_rows,
            source_basis_lookup,
        )
    )
    statements.extend(compile_literature_evidence(package.evidence_rows, source_document_ids))
    return statements


def compile_pack_timing_evidence(
    rows: list[InfluenzaPackTimingRow],
    source_basis_lookup: dict[str, str],
) -> list[EvidenceStatement]:
    statements: list[EvidenceStatement] = []
    for row in rows:
        statements.append(
            EvidenceStatement(
                evidence_statement_id=f"evidence_timing_{normalize_identifier(row.timing_parameter)}",
                statement=row.finding_text or row.codeblue_translation or row.timing_parameter,
                evidence_type="pathogen_timing_parameter",
                source_document_ids=resolve_source_basis_to_ids(
                    row.source_basis, source_basis_lookup
                ),
                confidence=confidence_from_note(row.confidence_note),
                uncertainty_note=row.confidence_note,
                applies_to=[
                    value for value in ["influenza", row.parameter_group, row.applies_to] if value
                ],
                used_by_rule_ids=[],
            )
        )
    return statements


def compile_pack_risk_feature_evidence(
    rows: list[InfluenzaPackRiskFeatureRow],
    source_basis_lookup: dict[str, str],
) -> list[EvidenceStatement]:
    statements: list[EvidenceStatement] = []
    for row in rows:
        statements.append(
            EvidenceStatement(
                evidence_statement_id=f"evidence_feature_{normalize_identifier(row.canonical_feature_name)}",
                statement=row.finding_text
                or row.codeblue_translation
                or row.canonical_feature_name,
                evidence_type="pathogen_risk_feature",
                source_document_ids=resolve_source_basis_to_ids(
                    row.source_basis, source_basis_lookup
                ),
                confidence=confidence_from_priority(row.priority_tier),
                uncertainty_note=row.caution_note,
                applies_to=[
                    value
                    for value in ["influenza", row.canonical_feature_name, row.default_use_stage]
                    if value
                ],
                used_by_rule_ids=[],
            )
        )
    return statements


def compile_pack_intervention_evidence(
    rows: list[InfluenzaPackInterventionRow],
    source_basis_lookup: dict[str, str],
) -> list[EvidenceStatement]:
    statements: list[EvidenceStatement] = []
    for row in rows:
        statements.append(
            EvidenceStatement(
                evidence_statement_id=f"evidence_intervention_{normalize_identifier(row.intervention_name)}",
                statement=row.finding_text or row.codeblue_translation or row.intervention_name,
                evidence_type="pathogen_intervention_hook",
                source_document_ids=resolve_source_basis_to_ids(
                    row.source_basis, source_basis_lookup
                ),
                confidence=ConfidenceLevel.MODERATE,
                uncertainty_note=row.operational_constraints,
                applies_to=[
                    value for value in ["influenza", row.action_type, row.target_entity] if value
                ],
                used_by_rule_ids=[],
            )
        )
    return statements


def compile_literature_evidence(
    rows: list[KnowledgeEvidenceRow],
    source_document_ids: set[str],
) -> list[EvidenceStatement]:
    statements: list[EvidenceStatement] = []
    for index, row in enumerate(rows, start=1):
        if (
            not row.finding_text
            and not row.codeblue_translation
            and not row.study_reported_implication
        ):
            continue
        doc_ids = [row.source_id] if row.source_id in source_document_ids else []
        statement = row.finding_text or row.codeblue_translation or row.study_reported_implication
        statements.append(
            EvidenceStatement(
                evidence_statement_id=f"evidence_lit_{index:04d}",
                statement=statement or f"Evidence row {index}",
                evidence_type=normalize_identifier(row.sheet_name),
                source_document_ids=doc_ids,
                confidence=confidence_from_text(row.evidence_strength),
                uncertainty_note=row.key_limitations,
                applies_to=[
                    value
                    for value in [
                        row.pathogen_scope,
                        row.canonical_feature_name,
                        row.temporal_stage,
                        row.outcome_linked,
                    ]
                    if value
                ],
                used_by_rule_ids=[],
            )
        )
    return statements


def compile_review_rules(
    *,
    trigger_action_mappings: list[TriggerActionMapping],
    trigger_index: dict[str, PolicyTriggerDefinition],
    action_index: dict[str, PolicyActionDefinition],
    workflow_pack_id: str,
) -> list[RuleArtifact]:
    rules: list[RuleArtifact] = []
    for mapping in trigger_action_mappings:
        trigger = trigger_index.get(mapping.trigger_id)
        action = action_index.get(mapping.action_id)
        if trigger is None or action is None or not trigger.trigger_fact_name:
            continue
        urgency = normalize_urgency(mapping.base_priority or trigger.priority)
        review_team = (
            mapping.review_role or action.human_review_role or action.default_owner or "review_team"
        )
        rules.append(
            RuleArtifact(
                rule_id=f"review_{mapping.map_id}",
                rule_kind=RuleKind.REVIEW_RULE,
                owner_pack_id=workflow_pack_id,
                name=f"{trigger.trigger_name} -> {action.action_name}",
                description=mapping.review_rationale
                or mapping.activation_logic
                or trigger.rationale,
                priority=priority_to_int(mapping.base_priority or trigger.priority),
                enabled=True,
                condition=RuleCondition(
                    fact=trigger.trigger_fact_name,
                    op=RuleOperator.EQ,
                    value=True,
                ),
                outputs=[
                    ProposedActionOutput(
                        type="proposed_action",
                        action_id=mapping.action_id,
                        review_team=review_team,
                        urgency=urgency,
                    )
                ],
                source_document_ids=trigger.source_document_ids,
                confidence=ConfidenceLevel.MODERATE,
                uncertainty_note=mapping.modifiers.suppression_logic,
                version="1.0.0",
            )
        )
    return rules


def compile_policy_constraint_rules(
    *,
    policy_action_catalog: list[PolicyActionDefinition],
    policy_pack_id: str,
) -> list[RuleArtifact]:
    rules: list[RuleArtifact] = []
    for action in policy_action_catalog:
        rules.append(
            RuleArtifact(
                rule_id=f"policy_review_only_{action.action_id}",
                rule_kind=RuleKind.POLICY_CONSTRAINT,
                owner_pack_id=policy_pack_id,
                name=f"{action.action_name} remains review only",
                description="Compiled from action review requirements in the source package.",
                priority=100,
                enabled=True,
                condition=RuleCondition(
                    fact="proposed_action.action_definition_id",
                    op=RuleOperator.EQ,
                    value=action.action_id,
                ),
                outputs=[
                    ConstraintOutput(
                        type="constraint",
                        key="execution_mode",
                        value=ExecutionMode.REVIEW_ONLY,
                    )
                ],
                source_document_ids=action.source_document_ids,
                confidence=ConfidenceLevel.HIGH,
                version="1.0.0",
            )
        )
        if action.audit_notes:
            rules.append(
                RuleArtifact(
                    rule_id=f"policy_audit_{action.action_id}",
                    rule_kind=RuleKind.POLICY_CONSTRAINT,
                    owner_pack_id=policy_pack_id,
                    name=f"{action.action_name} must be logged",
                    description="Compiled from action audit notes in the source package.",
                    priority=90,
                    enabled=True,
                    condition=RuleCondition(
                        fact="proposed_action.action_definition_id",
                        op=RuleOperator.EQ,
                        value=action.action_id,
                    ),
                    outputs=[
                        ConstraintOutput(
                            type="constraint",
                            key="audit_mode",
                            value="must_log",
                        )
                    ],
                    source_document_ids=action.source_document_ids,
                    confidence=ConfidenceLevel.MODERATE,
                    version="1.0.0",
                )
            )
    return rules


def compile_bundle_test_cases(
    trigger_action_mappings: list[TriggerActionMapping],
    trigger_index: dict[str, PolicyTriggerDefinition],
) -> list[KnowledgeTestCase]:
    grouped_mappings: dict[str, list[TriggerActionMapping]] = defaultdict(list)
    for mapping in trigger_action_mappings:
        grouped_mappings[mapping.trigger_id].append(mapping)

    scenarios = [
        "deployment_prealert_window_active",
        "respiratory_symptoms_at_arrival",
        "suspected_or_confirmed_inpatient_influenza",
    ]
    tests: list[KnowledgeTestCase] = []

    for trigger_id in scenarios:
        trigger = trigger_index.get(trigger_id)
        if trigger is None or not trigger.trigger_fact_name:
            continue
        mappings = grouped_mappings.get(trigger_id, [])
        tests.append(
            KnowledgeTestCase(
                test_case_id=f"tc_compiled_{trigger_id}",
                name=f"Compiled trigger case for {trigger_id}",
                input_facts={trigger.trigger_fact_name: True},
                expected_outputs=[
                    ProposedActionOutput(
                        type="proposed_action",
                        action_id=mapping.action_id,
                        review_team=mapping.review_role or "review_team",
                        urgency=normalize_urgency(mapping.base_priority or trigger.priority),
                    )
                    for mapping in mappings
                ],
                unexpected_outputs=[],
            )
        )

    return tests


def build_source_basis_lookup(rows: list[PolicySourceRow]) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for row in rows:
        aliases = {
            normalize_basis_token(row.policy_source_id),
            normalize_basis_token(row.source_title),
        }
        aliases.update(
            normalize_basis_token(alias)
            for alias in SOURCE_BASIS_ALIASES_BY_POLICY_SOURCE_ID.get(row.policy_source_id, set())
        )
        for alias in aliases:
            if alias:
                lookup[alias] = row.policy_source_id
    return lookup


def resolve_source_basis_to_ids(
    source_basis: str | None,
    source_basis_lookup: dict[str, str],
) -> list[str]:
    if not source_basis:
        return []
    resolved: list[str] = []
    for token in re.split(r"[;|]+", source_basis):
        normalized = normalize_basis_token(token)
        if not normalized:
            continue
        source_id = source_basis_lookup.get(normalized)
        if source_id and source_id not in resolved:
            resolved.append(source_id)
            continue
        for alias, candidate_id in source_basis_lookup.items():
            if normalized in alias or alias in normalized:
                if candidate_id not in resolved:
                    resolved.append(candidate_id)
                break
    return resolved


def normalize_action_target_scope(row: ActionLibraryRow) -> TargetScope:
    scope = (row.target_scope or "").lower()
    entity = (row.target_entity or "").lower()
    if scope in {"room", "room_and_care_team", "room_or_unit"}:
        return TargetScope.ROOM
    if scope in {"ward_or_unit"}:
        return TargetScope.WARD
    if scope in {"entry_points_waiting_areas_and_registration", "waiting_area_or_triage_zone"}:
        return TargetScope.ENTRY_POINT
    if scope in {"service_line_or_hospital", "facility_or_unit"}:
        return TargetScope.HOSPITAL
    if "hcp" in entity or "staff" in entity:
        return TargetScope.STAFF
    if scope in {
        "individual",
        "individual_or_exposure_group",
        "individual_or_schedule",
        "interdepartmental_transfer",
        "procedure_event",
    }:
        return TargetScope.PATIENT
    return TargetScope.HOSPITAL


def normalize_urgency(priority: str | None) -> str:
    value = (priority or "").strip().lower()
    if value in {"critical", "high"}:
        return "high"
    if value == "medium":
        return "medium"
    return "low"


def priority_to_int(priority: str | None) -> int:
    value = (priority or "").strip().lower()
    if value == "critical":
        return 130
    if value == "high":
        return 120
    if value == "medium":
        return 100
    return 80


def split_multi_value(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(";") if part.strip()]


def normalize_basis_token(value: str | None) -> str:
    if not value:
        return ""
    normalized = re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()
    return re.sub(r"\s+", " ", normalized)


def normalize_identifier(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def parse_full_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def infer_source_jurisdiction(row: PolicySourceRow) -> str:
    authority = (row.issuing_body or "").lower()
    if "cdc" in authority:
        return "US"
    if "brasil" in authority or "minist" in authority:
        return "Brazil"
    if "ceara" in authority or "sesa" in authority:
        return "Brazil/Ceara"
    return "generic"


def build_doi_url(doi: str | None) -> str | None:
    if not doi:
        return None
    if doi.startswith("http://") or doi.startswith("https://"):
        return doi
    return f"https://doi.org/{doi}"


def normalize_document_type(source_type: str) -> str:
    return source_type.replace("_", " ")


def confidence_from_note(note: str | None) -> ConfidenceLevel:
    text = (note or "").lower()
    if "strong" in text:
        return ConfidenceLevel.HIGH
    if "weak" in text or "limited" in text:
        return ConfidenceLevel.LOW
    return ConfidenceLevel.MODERATE


def confidence_from_priority(priority_tier: str | None) -> ConfidenceLevel:
    value = (priority_tier or "").lower()
    if value == "very_high":
        return ConfidenceLevel.HIGH
    if value in {"high", "medium"}:
        return ConfidenceLevel.MODERATE
    return ConfidenceLevel.LOW


def confidence_from_text(value: str | None) -> ConfidenceLevel:
    text = (value or "").lower()
    if text == "high":
        return ConfidenceLevel.HIGH
    if text == "low":
        return ConfidenceLevel.LOW
    return ConfidenceLevel.MODERATE
