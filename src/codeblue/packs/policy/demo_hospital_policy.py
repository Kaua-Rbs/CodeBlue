from __future__ import annotations

from uuid import uuid4

from codeblue.domain.governance_models import ExecutionMode, ProposedAction, TargetScope
from codeblue.domain.knowledge_models import (
    ActionDefinition,
    ConstraintOutput,
    KnowledgeBundle,
    ProposedActionOutput,
    RuleArtifact,
    RuleKind,
)
from codeblue.domain.knowledge_runtime_models import PolicyExecutionContext
from codeblue.domain.risk_models import RiskAssessment
from codeblue.packs.policy.base import PolicyPack
from codeblue.services.facts_bridge import KnowledgeFactsBridge
from codeblue.services.rule_evaluator import RuleEvaluator


class DemoHospitalPolicyPack(PolicyPack):
    pack_id = "policy_general_hospital_demo_v1"
    name = "Demo Hospital Knowledge-Backed Policy Pack"
    version = "1.0.0"
    workflow_pack_id = "workflow_general_demo_v1"

    def __init__(self, knowledge_bundle: KnowledgeBundle) -> None:
        self.knowledge_bundle = knowledge_bundle
        self.rule_evaluator = RuleEvaluator()
        self.facts_bridge = KnowledgeFactsBridge()

    def propose_actions(
        self,
        assessments: list[RiskAssessment],
        context: PolicyExecutionContext | None = None,
    ) -> list[ProposedAction]:
        review_rules = self.knowledge_bundle.rules_for_pack(
            self.workflow_pack_id,
            RuleKind.REVIEW_RULE,
        )
        policy_rules = self.knowledge_bundle.rules_for_pack(
            self.pack_id,
            RuleKind.POLICY_CONSTRAINT,
        )
        actions: list[ProposedAction] = []

        for assessment in assessments:
            review_evaluation = self.rule_evaluator.evaluate_rules(
                review_rules,
                self.facts_bridge.assessment_facts(assessment),
            )
            for output in review_evaluation.matched_outputs:
                if not isinstance(output, ProposedActionOutput):
                    continue
                action_definition = self.knowledge_bundle.action_definition(output.action_id)
                action = self._build_action(
                    action_definition=action_definition,
                    assessment=assessment,
                    review_rule_ids=review_evaluation.triggering_rule_ids,
                )
                self._apply_policy_constraints(action, policy_rules)
                actions.append(action)

        return actions

    def _build_action(
        self,
        action_definition: ActionDefinition,
        assessment: RiskAssessment,
        review_rule_ids: list[str],
    ) -> ProposedAction:
        target_id = assessment.target_id
        if action_definition.target_scope == TargetScope.ROOM:
            target_id = str(assessment.context_facts.get("target.room_id", assessment.target_id))
        elif action_definition.target_scope == TargetScope.WARD:
            target_id = str(assessment.context_facts.get("target.ward_id", assessment.target_id))

        return ProposedAction(
            risk_assessment_id=assessment.assessment_id,
            action_definition_id=action_definition.action_id,
            action_type=action_definition.subtype,
            category=action_definition.category,
            priority=assessment.priority,
            execution_mode=action_definition.execution_mode,
            target_scope=action_definition.target_scope,
            target_id=target_id,
            rationale=(
                f"Triggered by knowledge review rules for assessment '{assessment.assessment_id}'."
            ),
            required_reviewer_role=action_definition.requires_reviewer_role,
            constraints_applied=[f"execution_mode:{action_definition.execution_mode}"],
            knowledge_bundle_id=self.knowledge_bundle.bundle_id,
            triggering_rule_ids=assessment.triggering_rule_ids + review_rule_ids,
            audit_ref=uuid4(),
        )

    def _apply_policy_constraints(
        self,
        action: ProposedAction,
        policy_rules: list[RuleArtifact],
    ) -> None:
        facts = self.facts_bridge.action_facts(
            action_category=action.category,
            execution_mode=action.execution_mode,
            action_definition_id=action.action_definition_id,
        )
        evaluation = self.rule_evaluator.evaluate_rules(policy_rules, facts)
        for output in evaluation.matched_outputs:
            if not isinstance(output, ConstraintOutput):
                continue
            if output.key == "execution_mode":
                action.execution_mode = ExecutionMode(output.value)
            action.constraints_applied.append(f"{output.key}:{output.value}")
            if output.key == "execution_mode" and output.value == ExecutionMode.REVIEW_ONLY:
                action.constraints_applied.append("requires_human_review")
        if evaluation.triggering_rule_ids:
            action.triggering_rule_ids.extend(evaluation.triggering_rule_ids)
