from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from codeblue.domain.knowledge_models import (
    KnowledgeTestCase,
    RuleArtifact,
    RuleCondition,
    RuleOperator,
    RuleOutput,
)


@dataclass
class RuleMatch:
    rule_id: str
    outputs: list[RuleOutput]


@dataclass
class RuleEvaluationResult:
    matched_outputs: list[RuleOutput]
    triggering_rule_ids: list[str]
    matches: list[RuleMatch]


@dataclass
class KnowledgeTestResult:
    test_case_id: str
    passed: bool
    matched_outputs: list[RuleOutput]
    triggering_rule_ids: list[str]


class RuleEvaluator:
    def evaluate_rules(
        self,
        rules: list[RuleArtifact],
        facts: dict[str, Any],
    ) -> RuleEvaluationResult:
        matches: list[RuleMatch] = []
        for rule in sorted(rules, key=lambda item: item.priority, reverse=True):
            if not rule.enabled:
                continue
            if self._evaluate_condition(rule.condition, facts):
                matches.append(RuleMatch(rule_id=rule.rule_id, outputs=rule.outputs))

        return RuleEvaluationResult(
            matched_outputs=[output for match in matches for output in match.outputs],
            triggering_rule_ids=[match.rule_id for match in matches],
            matches=matches,
        )

    def run_test_case(
        self,
        rules: list[RuleArtifact],
        test_case: KnowledgeTestCase,
    ) -> KnowledgeTestResult:
        result = self.evaluate_rules(rules, test_case.input_facts)
        normalized_actual = [output.model_dump(mode="json") for output in result.matched_outputs]
        expected = [output.model_dump(mode="json") for output in test_case.expected_outputs]
        unexpected = [output.model_dump(mode="json") for output in test_case.unexpected_outputs]

        passed = all(item in normalized_actual for item in expected) and all(
            item not in normalized_actual for item in unexpected
        )
        return KnowledgeTestResult(
            test_case_id=test_case.test_case_id,
            passed=passed,
            matched_outputs=result.matched_outputs,
            triggering_rule_ids=result.triggering_rule_ids,
        )

    def _evaluate_condition(self, condition: RuleCondition, facts: dict[str, Any]) -> bool:
        if condition.all is not None:
            return all(self._evaluate_condition(child, facts) for child in condition.all)
        if condition.any is not None:
            return any(self._evaluate_condition(child, facts) for child in condition.any)
        if condition.not_ is not None:
            return not self._evaluate_condition(condition.not_, facts)
        assert condition.fact is not None
        assert condition.op is not None
        return self._evaluate_predicate(
            fact_value=facts.get(condition.fact),
            operator=condition.op,
            expected_value=condition.value,
            fact_exists=condition.fact in facts,
        )

    def _evaluate_predicate(
        self,
        fact_value: Any,
        operator: RuleOperator,
        expected_value: Any,
        fact_exists: bool,
    ) -> bool:
        if operator == RuleOperator.EXISTS:
            return fact_exists and fact_value is not None
        if not fact_exists:
            return False
        if operator == RuleOperator.EQ:
            return bool(fact_value == expected_value)
        if operator == RuleOperator.NEQ:
            return bool(fact_value != expected_value)
        if operator == RuleOperator.GT:
            return bool(fact_value > expected_value)
        if operator == RuleOperator.GTE:
            return bool(fact_value >= expected_value)
        if operator == RuleOperator.LT:
            return bool(fact_value < expected_value)
        if operator == RuleOperator.LTE:
            return bool(fact_value <= expected_value)
        if operator == RuleOperator.IN:
            if not isinstance(expected_value, list):
                raise ValueError("The 'in' operator requires a list value.")
            return bool(fact_value in expected_value)
        if operator == RuleOperator.CONTAINS:
            if isinstance(fact_value, (list, tuple, set, str)):
                return bool(expected_value in fact_value)
            return False
        if operator == RuleOperator.COUNT_GTE:
            if isinstance(fact_value, (list, tuple, set, dict, str)):
                return bool(len(fact_value) >= expected_value)
            if isinstance(fact_value, (int, float)):
                return bool(fact_value >= expected_value)
            return False
        raise ValueError(f"Unsupported operator '{operator}'.")
