from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from codeblue.domain.knowledge_models import (
    ActionDefinition,
    EvidenceStatement,
    KnowledgeBundle,
    KnowledgeTestCase,
    PathogenPack,
    PolicyPack,
    ReviewWorkflowPack,
    RuleArtifact,
    SourceDocument,
    TerminologyBinding,
)
from codeblue.persistence.orm_models import (
    ActionDefinitionRecord,
    EvidenceStatementRecord,
    KnowledgeBundleRecord,
    KnowledgeTestCaseRecord,
    PathogenPackRecord,
    PolicyPackRecord,
    ReviewWorkflowPackRecord,
    RuleArtifactRecord,
    SourceDocumentRecord,
    TerminologyBindingRecord,
)


class KnowledgeRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def replace_bundle(self, bundle: KnowledgeBundle) -> KnowledgeBundle:
        self.session.execute(
            delete(SourceDocumentRecord).where(SourceDocumentRecord.bundle_id == bundle.bundle_id)
        )
        self.session.execute(
            delete(PathogenPackRecord).where(PathogenPackRecord.bundle_id == bundle.bundle_id)
        )
        self.session.execute(
            delete(PolicyPackRecord).where(PolicyPackRecord.bundle_id == bundle.bundle_id)
        )
        self.session.execute(
            delete(ReviewWorkflowPackRecord).where(
                ReviewWorkflowPackRecord.bundle_id == bundle.bundle_id
            )
        )
        self.session.execute(
            delete(ActionDefinitionRecord).where(
                ActionDefinitionRecord.bundle_id == bundle.bundle_id
            )
        )
        self.session.execute(
            delete(EvidenceStatementRecord).where(
                EvidenceStatementRecord.bundle_id == bundle.bundle_id
            )
        )
        self.session.execute(
            delete(TerminologyBindingRecord).where(
                TerminologyBindingRecord.bundle_id == bundle.bundle_id
            )
        )
        self.session.execute(
            delete(RuleArtifactRecord).where(RuleArtifactRecord.bundle_id == bundle.bundle_id)
        )
        self.session.execute(
            delete(KnowledgeTestCaseRecord).where(
                KnowledgeTestCaseRecord.bundle_id == bundle.bundle_id
            )
        )
        self.session.execute(
            delete(KnowledgeBundleRecord).where(KnowledgeBundleRecord.bundle_id == bundle.bundle_id)
        )
        self.session.flush()

        self.session.add(
            KnowledgeBundleRecord(
                bundle_id=bundle.bundle_id,
                name=bundle.name,
                version=bundle.version,
                status=bundle.status,
                created_at=bundle.created_at,
                updated_at=bundle.updated_at,
                jurisdiction=bundle.jurisdiction,
                organization=bundle.organization,
                description=bundle.description,
            )
        )

        for document in bundle.source_documents:
            self.session.add(
                SourceDocumentRecord(
                    bundle_id=bundle.bundle_id,
                    source_document_id=document.source_document_id,
                    title=document.title,
                    organization=document.organization,
                    document_type=document.document_type,
                    publication_date=(
                        document.publication_date.isoformat()
                        if document.publication_date is not None
                        else None
                    ),
                    version_label=document.version_label,
                    jurisdiction=document.jurisdiction,
                    setting_scope=document.setting_scope,
                    url=document.url,
                    language=document.language,
                    machine_readability=document.machine_readability,
                    ingestion_mode=document.ingestion_mode,
                    notes=document.notes,
                )
            )

        for pack in bundle.pathogen_packs:
            self.session.add(
                PathogenPackRecord(
                    bundle_id=bundle.bundle_id,
                    pathogen_pack_id=pack.pathogen_pack_id,
                    pathogen_code=pack.pathogen_code,
                    display_name=pack.display_name,
                    version=pack.version,
                    status=pack.status,
                    source_document_ids=pack.source_document_ids,
                    notes=pack.notes,
                )
            )

        for pack in bundle.policy_packs:
            self.session.add(
                PolicyPackRecord(
                    bundle_id=bundle.bundle_id,
                    policy_pack_id=pack.policy_pack_id,
                    name=pack.name,
                    version=pack.version,
                    jurisdiction=pack.jurisdiction,
                    organization=pack.organization,
                    source_document_ids=pack.source_document_ids,
                )
            )

        for pack in bundle.review_workflow_packs:
            self.session.add(
                ReviewWorkflowPackRecord(
                    bundle_id=bundle.bundle_id,
                    workflow_pack_id=pack.workflow_pack_id,
                    name=pack.name,
                    version=pack.version,
                    source_document_ids=pack.source_document_ids,
                )
            )

        for action in bundle.action_catalog:
            self.session.add(
                ActionDefinitionRecord(
                    bundle_id=bundle.bundle_id,
                    action_id=action.action_id,
                    display_name=action.display_name,
                    category=action.category,
                    subtype=action.subtype,
                    description=action.description,
                    pathogen_specificity=action.pathogen_specificity,
                    execution_mode=action.execution_mode,
                    requires_reviewer_role=action.requires_reviewer_role,
                    target_scope=action.target_scope,
                    must_be_logged=action.must_be_logged,
                )
            )

        for evidence in bundle.evidence_statements:
            self.session.add(
                EvidenceStatementRecord(
                    bundle_id=bundle.bundle_id,
                    evidence_statement_id=evidence.evidence_statement_id,
                    statement=evidence.statement,
                    evidence_type=evidence.evidence_type,
                    source_document_ids=evidence.source_document_ids,
                    confidence=evidence.confidence,
                    uncertainty_note=evidence.uncertainty_note,
                    applies_to=evidence.applies_to,
                    used_by_rule_ids=evidence.used_by_rule_ids,
                )
            )

        for binding in bundle.terminology_bindings:
            self.session.add(
                TerminologyBindingRecord(
                    bundle_id=bundle.bundle_id,
                    binding_id=binding.binding_id,
                    local_system=binding.local_system,
                    local_code=binding.local_code,
                    local_display=binding.local_display,
                    canonical_field=binding.canonical_field,
                    canonical_value=binding.canonical_value,
                )
            )

        for rule in bundle.rule_artifacts:
            self.session.add(
                RuleArtifactRecord(
                    bundle_id=bundle.bundle_id,
                    rule_id=rule.rule_id,
                    rule_kind=rule.rule_kind,
                    owner_pack_id=rule.owner_pack_id,
                    name=rule.name,
                    description=rule.description,
                    priority=rule.priority,
                    enabled=rule.enabled,
                    condition_payload=rule.condition.model_dump(mode="json", by_alias=True),
                    outputs_payload=[output.model_dump(mode="json") for output in rule.outputs],
                    source_document_ids=rule.source_document_ids,
                    confidence=rule.confidence,
                    uncertainty_note=rule.uncertainty_note,
                    version=rule.version,
                )
            )

        for test_case in bundle.test_cases:
            self.session.add(
                KnowledgeTestCaseRecord(
                    bundle_id=bundle.bundle_id,
                    test_case_id=test_case.test_case_id,
                    name=test_case.name,
                    input_facts=test_case.input_facts,
                    expected_outputs=[
                        output.model_dump(mode="json") for output in test_case.expected_outputs
                    ],
                    unexpected_outputs=[
                        output.model_dump(mode="json") for output in test_case.unexpected_outputs
                    ],
                )
            )

        self.session.commit()
        return bundle

    def get_bundle(self, bundle_id: str) -> KnowledgeBundle | None:
        bundle_record = self.session.get(KnowledgeBundleRecord, bundle_id)
        if bundle_record is None:
            return None

        source_documents = self.session.scalars(
            select(SourceDocumentRecord).where(SourceDocumentRecord.bundle_id == bundle_id)
        ).all()
        pathogen_packs = self.session.scalars(
            select(PathogenPackRecord).where(PathogenPackRecord.bundle_id == bundle_id)
        ).all()
        policy_packs = self.session.scalars(
            select(PolicyPackRecord).where(PolicyPackRecord.bundle_id == bundle_id)
        ).all()
        workflow_packs = self.session.scalars(
            select(ReviewWorkflowPackRecord).where(ReviewWorkflowPackRecord.bundle_id == bundle_id)
        ).all()
        action_definitions = self.session.scalars(
            select(ActionDefinitionRecord).where(ActionDefinitionRecord.bundle_id == bundle_id)
        ).all()
        evidence_statements = self.session.scalars(
            select(EvidenceStatementRecord).where(EvidenceStatementRecord.bundle_id == bundle_id)
        ).all()
        terminology_bindings = self.session.scalars(
            select(TerminologyBindingRecord).where(TerminologyBindingRecord.bundle_id == bundle_id)
        ).all()
        rule_artifacts = self.session.scalars(
            select(RuleArtifactRecord).where(RuleArtifactRecord.bundle_id == bundle_id)
        ).all()
        test_cases = self.session.scalars(
            select(KnowledgeTestCaseRecord).where(KnowledgeTestCaseRecord.bundle_id == bundle_id)
        ).all()

        return KnowledgeBundle.model_validate(
            {
                "bundle_id": bundle_record.bundle_id,
                "name": bundle_record.name,
                "version": bundle_record.version,
                "status": bundle_record.status,
                "created_at": bundle_record.created_at,
                "updated_at": bundle_record.updated_at,
                "jurisdiction": bundle_record.jurisdiction,
                "organization": bundle_record.organization,
                "description": bundle_record.description,
                "source_documents": [
                    SourceDocument.model_validate(
                        {
                            "source_document_id": record.source_document_id,
                            "title": record.title,
                            "organization": record.organization,
                            "document_type": record.document_type,
                            "publication_date": record.publication_date,
                            "version_label": record.version_label,
                            "jurisdiction": record.jurisdiction,
                            "setting_scope": record.setting_scope,
                            "url": record.url,
                            "language": record.language,
                            "machine_readability": record.machine_readability,
                            "ingestion_mode": record.ingestion_mode,
                            "notes": record.notes,
                        }
                    )
                    for record in source_documents
                ],
                "pathogen_packs": [
                    PathogenPack.model_validate(
                        {
                            "pathogen_pack_id": record.pathogen_pack_id,
                            "pathogen_code": record.pathogen_code,
                            "display_name": record.display_name,
                            "version": record.version,
                            "status": record.status,
                            "source_document_ids": record.source_document_ids,
                            "notes": record.notes,
                        }
                    )
                    for record in pathogen_packs
                ],
                "policy_packs": [
                    PolicyPack.model_validate(
                        {
                            "policy_pack_id": record.policy_pack_id,
                            "name": record.name,
                            "version": record.version,
                            "jurisdiction": record.jurisdiction,
                            "organization": record.organization,
                            "source_document_ids": record.source_document_ids,
                        }
                    )
                    for record in policy_packs
                ],
                "review_workflow_packs": [
                    ReviewWorkflowPack.model_validate(
                        {
                            "workflow_pack_id": record.workflow_pack_id,
                            "name": record.name,
                            "version": record.version,
                            "source_document_ids": record.source_document_ids,
                        }
                    )
                    for record in workflow_packs
                ],
                "action_catalog": [
                    ActionDefinition.model_validate(
                        {
                            "action_id": record.action_id,
                            "display_name": record.display_name,
                            "category": record.category,
                            "subtype": record.subtype,
                            "description": record.description,
                            "pathogen_specificity": record.pathogen_specificity,
                            "execution_mode": record.execution_mode,
                            "requires_reviewer_role": record.requires_reviewer_role,
                            "target_scope": record.target_scope,
                            "must_be_logged": record.must_be_logged,
                        }
                    )
                    for record in action_definitions
                ],
                "evidence_statements": [
                    EvidenceStatement.model_validate(
                        {
                            "evidence_statement_id": record.evidence_statement_id,
                            "statement": record.statement,
                            "evidence_type": record.evidence_type,
                            "source_document_ids": record.source_document_ids,
                            "confidence": record.confidence,
                            "uncertainty_note": record.uncertainty_note,
                            "applies_to": record.applies_to,
                            "used_by_rule_ids": record.used_by_rule_ids,
                        }
                    )
                    for record in evidence_statements
                ],
                "terminology_bindings": [
                    TerminologyBinding.model_validate(
                        {
                            "binding_id": record.binding_id,
                            "local_system": record.local_system,
                            "local_code": record.local_code,
                            "local_display": record.local_display,
                            "canonical_field": record.canonical_field,
                            "canonical_value": record.canonical_value,
                        }
                    )
                    for record in terminology_bindings
                ],
                "rule_artifacts": [
                    RuleArtifact.model_validate(
                        {
                            "rule_id": record.rule_id,
                            "rule_kind": record.rule_kind,
                            "owner_pack_id": record.owner_pack_id,
                            "name": record.name,
                            "description": record.description,
                            "priority": record.priority,
                            "enabled": record.enabled,
                            "condition": record.condition_payload,
                            "outputs": record.outputs_payload,
                            "source_document_ids": record.source_document_ids,
                            "confidence": record.confidence,
                            "uncertainty_note": record.uncertainty_note,
                            "version": record.version,
                        }
                    )
                    for record in rule_artifacts
                ],
                "test_cases": [
                    KnowledgeTestCase.model_validate(
                        {
                            "test_case_id": record.test_case_id,
                            "name": record.name,
                            "input_facts": record.input_facts,
                            "expected_outputs": record.expected_outputs,
                            "unexpected_outputs": record.unexpected_outputs,
                        }
                    )
                    for record in test_cases
                ],
            }
        )
