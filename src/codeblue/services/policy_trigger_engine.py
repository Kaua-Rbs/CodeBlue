from __future__ import annotations

from codeblue.domain.knowledge_runtime_models import (
    PolicyExecutionContext,
    PolicyTriggerDefinition,
    TriggerMatch,
)

SUPPORTED_TRIGGER_IDS = {
    "deployment_prealert_window_active",
    "deployment_high_alert_window_active",
    "respiratory_symptoms_at_arrival",
    "suspected_or_confirmed_inpatient_influenza",
    "ward_cluster_signal",
}


class PolicyTriggerEngine:
    def evaluate(
        self,
        triggers: list[PolicyTriggerDefinition],
        context: PolicyExecutionContext,
    ) -> list[TriggerMatch]:
        matches: list[TriggerMatch] = []
        facts = context.runtime_facts

        for trigger in triggers:
            if trigger.trigger_id not in SUPPORTED_TRIGGER_IDS or not trigger.trigger_fact_name:
                continue

            fact_value = facts.get(trigger.trigger_fact_name)
            if trigger.trigger_id in {
                "deployment_prealert_window_active",
                "deployment_high_alert_window_active",
            }:
                if isinstance(fact_value, dict) and fact_value.get("matched"):
                    matches.append(
                        TriggerMatch(
                            trigger_id=trigger.trigger_id,
                            trigger_name=trigger.trigger_name,
                            fact_name=trigger.trigger_fact_name,
                            target_scope="hospital",
                            target_id=context.hospital_id,
                            facts_used={trigger.trigger_fact_name: fact_value},
                        )
                    )
                continue

            if not isinstance(fact_value, dict):
                continue

            target_scope = "ward" if trigger.trigger_id == "ward_cluster_signal" else "patient"
            for target_id, details in fact_value.items():
                if not isinstance(details, dict) or not details.get("matched"):
                    continue
                matches.append(
                    TriggerMatch(
                        trigger_id=trigger.trigger_id,
                        trigger_name=trigger.trigger_name,
                        fact_name=trigger.trigger_fact_name,
                        target_scope=target_scope,
                        target_id=target_id,
                        facts_used={trigger.trigger_fact_name: details},
                    )
                )

        return matches
