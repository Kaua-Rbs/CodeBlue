from __future__ import annotations

from codeblue.domain.governance_models import ExecutionMode, ProposedAction
from codeblue.domain.knowledge_models import ConstraintOutput, RuleArtifact, RuleKind
from codeblue.domain.knowledge_runtime_models import (
    CompiledKnowledgePackage,
    PolicyExecutionContext,
)
from codeblue.domain.risk_models import RiskAssessment
from codeblue.packs.policy.base import PolicyPack
from codeblue.services.facts_bridge import KnowledgeFactsBridge
from codeblue.services.policy_trigger_engine import PolicyTriggerEngine
from codeblue.services.rule_evaluator import RuleEvaluator
from codeblue.services.trigger_action_mapper import TriggerActionMapper


class CompiledWorkbookPolicyPack(PolicyPack):
    version = "compiled-workbook-policy:1.0.0"

    def __init__(self, compiled_package: CompiledKnowledgePackage) -> None:
        self.compiled_package = compiled_package
        self.pack_id = self.compiled_package.knowledge_bundle.policy_packs[0].policy_pack_id
        self.name = self.compiled_package.knowledge_bundle.policy_packs[0].name
        self.rule_evaluator = RuleEvaluator()
        self.facts_bridge = KnowledgeFactsBridge()
        self.trigger_engine = PolicyTriggerEngine()
        self.action_mapper = TriggerActionMapper()
        self.policy_rules = self.compiled_package.knowledge_bundle.rules_for_pack(
            self.pack_id,
            RuleKind.POLICY_CONSTRAINT,
        )
        self.trigger_index = {
            trigger.trigger_id: trigger for trigger in self.compiled_package.policy_triggers
        }
        self.action_index = {
            action.action_id: action for action in self.compiled_package.policy_action_catalog
        }

    def propose_actions(
        self,
        assessments: list[RiskAssessment],
        context: PolicyExecutionContext | None = None,
    ) -> list[ProposedAction]:
        if context is None:
            return []

        context.matched_triggers = self.trigger_engine.evaluate(
            self.compiled_package.policy_triggers,
            context,
        )
        actions = self.action_mapper.map_actions(
            trigger_matches=context.matched_triggers,
            trigger_index=self.trigger_index,
            action_index=self.action_index,
            mappings=self.compiled_package.trigger_action_mappings,
            context=context,
        )

        for action in actions:
            self._apply_policy_constraints(action, self.policy_rules)
        return actions

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
            action.triggering_rule_ids.extend(
                rule_id
                for rule_id in evaluation.triggering_rule_ids
                if rule_id not in action.triggering_rule_ids
            )
