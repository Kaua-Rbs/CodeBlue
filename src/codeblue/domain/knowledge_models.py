from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from codeblue.domain.governance_models import ExecutionMode, TargetScope


class KnowledgeModel(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)


class BundleStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class ConfidenceLevel(StrEnum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class RuleKind(StrEnum):
    CASE_DEFINITION = "case_definition"
    TRANSMISSION = "transmission"
    POLICY_CONSTRAINT = "policy_constraint"
    REVIEW_RULE = "review_rule"
    ESCALATION_RULE = "escalation_rule"


class RuleOperator(StrEnum):
    EQ = "eq"
    NEQ = "neq"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    IN = "in"
    CONTAINS = "contains"
    EXISTS = "exists"
    COUNT_GTE = "count_gte"


class MachineReadability(StrEnum):
    PROSE = "prose"
    SEMI_STRUCTURED = "semi_structured"
    STRUCTURED = "structured"
    COMPUTABLE = "computable"


class IngestionMode(StrEnum):
    MANUAL_STRUCTURING = "manual_structuring"
    TEMPLATE_IMPORT = "template_import"
    DIRECT_IMPORT = "direct_import"


class RuleCondition(KnowledgeModel):
    all: list["RuleCondition"] | None = None
    any: list["RuleCondition"] | None = None
    not_: "RuleCondition | None" = Field(default=None, alias="not")
    fact: str | None = None
    op: RuleOperator | None = None
    value: Any | None = None

    @model_validator(mode="after")
    def validate_shape(self) -> "RuleCondition":
        shapes = [
            self.all is not None,
            self.any is not None,
            self.not_ is not None,
            self.fact is not None or self.op is not None or self.value is not None,
        ]
        if sum(bool(shape) for shape in shapes) != 1:
            raise ValueError("RuleCondition must define exactly one condition shape.")

        if self.fact is not None and self.op is None:
            raise ValueError("Predicate conditions require an operator.")
        if self.op is not None and self.fact is None:
            raise ValueError("Predicate conditions require a fact.")
        if self.op == RuleOperator.EXISTS and self.value is not None:
            raise ValueError("The 'exists' operator does not accept a value.")
        if self.op != RuleOperator.EXISTS and self.fact is not None and self.value is None:
            raise ValueError("Predicate conditions require a value unless using 'exists'.")
        if self.all is not None and len(self.all) == 0:
            raise ValueError("'all' conditions must contain at least one child.")
        if self.any is not None and len(self.any) == 0:
            raise ValueError("'any' conditions must contain at least one child.")
        return self


class ClassificationOutput(KnowledgeModel):
    type: Literal["classification"]
    key: str
    value: str


class ExposureFlagOutput(KnowledgeModel):
    type: Literal["exposure_flag"]
    key: str
    value: str


class ConstraintOutput(KnowledgeModel):
    type: Literal["constraint"]
    key: str
    value: str


class ProposedActionOutput(KnowledgeModel):
    type: Literal["proposed_action"]
    action_id: str
    review_team: str
    urgency: str


class NotificationRouteOutput(KnowledgeModel):
    type: Literal["notification_route"]
    review_team: str
    urgency: str


RuleOutput = Annotated[
    ClassificationOutput
    | ExposureFlagOutput
    | ConstraintOutput
    | ProposedActionOutput
    | NotificationRouteOutput,
    Field(discriminator="type"),
]


class SourceDocument(KnowledgeModel):
    source_document_id: str
    title: str
    organization: str
    document_type: str
    publication_date: date | None = None
    version_label: str | None = None
    jurisdiction: str
    setting_scope: list[str] = Field(default_factory=list)
    url: str | None = None
    language: str = "en"
    machine_readability: MachineReadability
    ingestion_mode: IngestionMode
    notes: str | None = None


class PathogenPack(KnowledgeModel):
    pathogen_pack_id: str
    pathogen_code: str
    display_name: str
    version: str
    status: BundleStatus
    source_document_ids: list[str] = Field(default_factory=list)
    notes: str | None = None


class PolicyPack(KnowledgeModel):
    policy_pack_id: str
    name: str
    version: str
    jurisdiction: str
    organization: str
    source_document_ids: list[str] = Field(default_factory=list)


class ReviewWorkflowPack(KnowledgeModel):
    workflow_pack_id: str
    name: str
    version: str
    source_document_ids: list[str] = Field(default_factory=list)


class ActionDefinition(KnowledgeModel):
    action_id: str
    display_name: str
    category: str
    subtype: str
    description: str
    pathogen_specificity: list[str] = Field(default_factory=list)
    execution_mode: ExecutionMode = ExecutionMode.REVIEW_ONLY
    requires_reviewer_role: str
    target_scope: TargetScope
    must_be_logged: bool = True


class EvidenceStatement(KnowledgeModel):
    evidence_statement_id: str
    statement: str
    evidence_type: str
    source_document_ids: list[str] = Field(default_factory=list)
    confidence: ConfidenceLevel
    uncertainty_note: str | None = None
    applies_to: list[str] = Field(default_factory=list)
    used_by_rule_ids: list[str] = Field(default_factory=list)


class TerminologyBinding(KnowledgeModel):
    binding_id: str
    local_system: str
    local_code: str
    local_display: str
    canonical_field: str
    canonical_value: str


class RuleArtifact(KnowledgeModel):
    rule_id: str
    rule_kind: RuleKind
    owner_pack_id: str
    name: str
    description: str | None = None
    priority: int = 100
    enabled: bool = True
    condition: RuleCondition
    outputs: list[RuleOutput]
    source_document_ids: list[str] = Field(default_factory=list)
    confidence: ConfidenceLevel | None = None
    uncertainty_note: str | None = None
    version: str = "1.0.0"


class KnowledgeTestCase(KnowledgeModel):
    test_case_id: str
    name: str
    input_facts: dict[str, Any]
    expected_outputs: list[RuleOutput] = Field(default_factory=list)
    unexpected_outputs: list[RuleOutput] = Field(default_factory=list)


class KnowledgeBundle(KnowledgeModel):
    bundle_id: str
    name: str
    version: str
    status: BundleStatus
    created_at: datetime
    updated_at: datetime
    jurisdiction: str
    organization: str
    description: str
    source_documents: list[SourceDocument] = Field(default_factory=list)
    terminology_bindings: list[TerminologyBinding] = Field(default_factory=list)
    pathogen_packs: list[PathogenPack] = Field(default_factory=list)
    policy_packs: list[PolicyPack] = Field(default_factory=list)
    review_workflow_packs: list[ReviewWorkflowPack] = Field(default_factory=list)
    evidence_statements: list[EvidenceStatement] = Field(default_factory=list)
    rule_artifacts: list[RuleArtifact] = Field(default_factory=list)
    action_catalog: list[ActionDefinition] = Field(default_factory=list)
    test_cases: list[KnowledgeTestCase] = Field(default_factory=list)

    def pathogen_pack(self, pack_id: str) -> PathogenPack:
        return next(pack for pack in self.pathogen_packs if pack.pathogen_pack_id == pack_id)

    def policy_pack(self, pack_id: str) -> PolicyPack:
        return next(pack for pack in self.policy_packs if pack.policy_pack_id == pack_id)

    def workflow_pack(self, pack_id: str) -> ReviewWorkflowPack:
        return next(pack for pack in self.review_workflow_packs if pack.workflow_pack_id == pack_id)

    def action_definition(self, action_id: str) -> ActionDefinition:
        return next(action for action in self.action_catalog if action.action_id == action_id)

    def rules_for_pack(self, pack_id: str, rule_kind: RuleKind | None = None) -> list[RuleArtifact]:
        rules = [rule for rule in self.rule_artifacts if rule.owner_pack_id == pack_id]
        if rule_kind is None:
            return sorted(rules, key=lambda rule: rule.priority, reverse=True)
        return sorted(
            [rule for rule in rules if rule.rule_kind == rule_kind],
            key=lambda rule: rule.priority,
            reverse=True,
        )


RuleCondition.model_rebuild()
