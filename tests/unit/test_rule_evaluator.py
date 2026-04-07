from __future__ import annotations

from codeblue.services.knowledge_loader import load_knowledge_bundle
from codeblue.services.rule_evaluator import RuleEvaluator


def test_rule_evaluator_handles_nested_logic() -> None:
    evaluator = RuleEvaluator()
    bundle = load_knowledge_bundle()
    rule = next(
        rule for rule in bundle.rule_artifacts if rule.rule_id == "rule_influenza_hospital_onset_case"
    )

    result = evaluator.evaluate_rules(
        [rule],
        {
            "lab.confirmed_pathogen": "influenza",
            "encounter.hours_since_admission": 120,
        },
    )

    assert result.triggering_rule_ids == ["rule_influenza_hospital_onset_case"]
    assert result.matched_outputs[0].type == "classification"


def test_knowledge_test_case_executes_deterministically() -> None:
    evaluator = RuleEvaluator()
    bundle = load_knowledge_bundle()
    rules = bundle.rules_for_pack("pathogen_influenza_a_v1")
    test_case = next(
        case for case in bundle.test_cases if case.test_case_id == "tc_influenza_hospital_onset_001"
    )

    result = evaluator.run_test_case(rules, test_case)

    assert result.passed is True


def test_review_rule_emits_proposed_action_output() -> None:
    evaluator = RuleEvaluator()
    bundle = load_knowledge_bundle()
    rules = bundle.rules_for_pack("workflow_general_demo_v1")

    result = evaluator.evaluate_rules(
        rules,
        {"classification.case_classification": "hospital_onset_influenza"},
    )

    assert result.triggering_rule_ids == [
        "review_isolation_placement_for_hospital_onset_influenza"
    ]
    assert result.matched_outputs[0].type == "proposed_action"


def test_policy_constraint_rule_constrains_medication_actions() -> None:
    evaluator = RuleEvaluator()
    bundle = load_knowledge_bundle()
    rules = bundle.rules_for_pack("policy_general_hospital_demo_v1")
    test_case = next(
        case
        for case in bundle.test_cases
        if case.test_case_id == "tc_policy_medication_review_only_001"
    )

    result = evaluator.run_test_case(rules, test_case)

    assert result.passed is True
