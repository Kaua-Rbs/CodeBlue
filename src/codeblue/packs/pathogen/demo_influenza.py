from __future__ import annotations

from codeblue.domain.canonical_events import EventEnvelope
from codeblue.domain.knowledge_models import KnowledgeBundle, RuleKind
from codeblue.domain.risk_models import (
    EntityScope,
    PriorityAlert,
    RiskAssessment,
    RiskPriority,
    RiskSignal,
)
from codeblue.domain.state_models import StateSnapshotRef, TimeWindow
from codeblue.packs.pathogen.base import PathogenPack
from codeblue.services.facts_bridge import KnowledgeFactsBridge
from codeblue.services.rule_evaluator import RuleEvaluator


def _priority_for_classification(classification: str) -> RiskPriority:
    if classification == "hospital_onset_influenza":
        return RiskPriority.HIGH
    return RiskPriority.MEDIUM


class DemoInfluenzaPathogenPack(PathogenPack):
    pack_id = "pathogen_influenza_a_v1"
    name = "Demo Influenza Knowledge-Backed Pathogen Pack"
    version = "1.0.0"

    def __init__(self, knowledge_bundle: KnowledgeBundle) -> None:
        self.knowledge_bundle = knowledge_bundle
        self.rule_evaluator = RuleEvaluator()
        self.facts_bridge = KnowledgeFactsBridge()

    def assess(
        self,
        events: list[EventEnvelope],
        snapshot: StateSnapshotRef,
        time_window: TimeWindow,
        policy_pack_version: str,
        scoring_version: str,
    ) -> tuple[list[RiskAssessment], list[PriorityAlert]]:
        rules = self.knowledge_bundle.rules_for_pack(self.pack_id, RuleKind.CASE_DEFINITION)
        assessments: list[RiskAssessment] = []
        alerts: list[PriorityAlert] = []

        for patient_state in snapshot.patient_states:
            facts = self.facts_bridge.patient_facts(events, snapshot, patient_state)
            evaluation = self.rule_evaluator.evaluate_rules(rules, facts)
            if not evaluation.triggering_rule_ids:
                continue

            classifications = {
                output.key: output.value
                for output in evaluation.matched_outputs
                if output.type == "classification"
            }
            case_classification = classifications.get("case_classification")
            if case_classification is None:
                continue

            priority = _priority_for_classification(case_classification)
            score = 0.85 if priority == RiskPriority.HIGH else 0.55
            signal = RiskSignal(
                name="case_definition_match",
                value=score,
                weight=1.0,
                explanation=(
                    f"Patient matched case definition '{case_classification}' via knowledge rules."
                ),
            )
            assessment = RiskAssessment(
                entity_scope=EntityScope.PATIENT,
                target_id=patient_state.patient_id,
                time_window=time_window,
                score=score,
                priority=priority,
                contributing_signals=[signal],
                generated_by=scoring_version,
                pathogen_pack_version=self.version,
                policy_pack_version=policy_pack_version,
                knowledge_bundle_id=self.knowledge_bundle.bundle_id,
                triggering_rule_ids=evaluation.triggering_rule_ids,
                context_facts={
                    **facts,
                    "classification.case_classification": case_classification,
                    "target.patient_id": patient_state.patient_id,
                    "target.room_id": patient_state.room_id,
                    "target.ward_id": patient_state.ward_id,
                },
            )
            assessments.append(assessment)
            alerts.append(
                PriorityAlert(
                    assessment_id=assessment.assessment_id,
                    target_id=patient_state.patient_id,
                    priority=priority,
                    summary=(
                        f"Patient {patient_state.patient_id} matched '{case_classification}' "
                        "and requires outbreak review."
                    ),
                    top_signals=[signal.name],
                )
            )

        return assessments, alerts
