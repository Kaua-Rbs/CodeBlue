from __future__ import annotations

from collections import defaultdict
from uuid import uuid4

from codeblue.domain.governance_models import ExecutionMode, ProposedAction, TargetScope
from codeblue.domain.knowledge_runtime_models import (
    PolicyActionDefinition,
    PolicyExecutionContext,
    PolicyTriggerDefinition,
    TriggerActionMapping,
    TriggerMatch,
)
from codeblue.domain.risk_models import RiskPriority

RELATIONSHIP_ORDER = {"required": 0, "recommended": 1, "conditional": 2}
TARGET_ORDER = {
    TargetScope.PATIENT: 0,
    TargetScope.ROOM: 1,
    TargetScope.WARD: 2,
    TargetScope.HOSPITAL: 3,
    TargetScope.ENTRY_POINT: 4,
}
PRIORITY_ORDER = {
    RiskPriority.CRITICAL: 0,
    RiskPriority.HIGH: 1,
    RiskPriority.MEDIUM: 2,
    RiskPriority.LOW: 3,
}


def action_trace_key(action_definition_id: str | None, target_scope: str, target_id: str) -> str:
    return f"{action_definition_id or 'unknown'}|{target_scope}|{target_id}"


class TriggerActionMapper:
    def map_actions(
        self,
        *,
        trigger_matches: list[TriggerMatch],
        trigger_index: dict[str, PolicyTriggerDefinition],
        action_index: dict[str, PolicyActionDefinition],
        mappings: list[TriggerActionMapping],
        context: PolicyExecutionContext,
    ) -> list[ProposedAction]:
        mappings_by_trigger: dict[str, list[TriggerActionMapping]] = defaultdict(list)
        for mapping in mappings:
            mappings_by_trigger[mapping.trigger_id].append(mapping)

        actions_by_key: dict[str, ProposedAction] = {}
        sort_metadata: dict[str, tuple[int, int, int]] = {}

        for match in trigger_matches:
            trigger = trigger_index.get(match.trigger_id)
            if trigger is None:
                continue
            for mapping in mappings_by_trigger.get(match.trigger_id, []):
                action_definition = action_index.get(mapping.action_id)
                if action_definition is None:
                    continue
                resolved_target_id = self._resolve_target_id(
                    action_definition.normalized_target_scope,
                    match,
                    context,
                )
                if resolved_target_id is None:
                    continue

                priority = self._priority_from_text(mapping.base_priority or trigger.priority)
                action = ProposedAction(
                    action_definition_id=action_definition.action_id,
                    action_type=action_definition.action_name,
                    category=action_definition.action_domain,
                    priority=priority,
                    execution_mode=ExecutionMode.REVIEW_ONLY,
                    target_scope=action_definition.normalized_target_scope,
                    target_id=resolved_target_id,
                    rationale=(
                        mapping.review_rationale
                        or trigger.rationale
                        or action_definition.action_description
                        or action_definition.action_name
                    ),
                    required_reviewer_role=(
                        mapping.review_role
                        or action_definition.human_review_role
                        or action_definition.default_owner
                        or "review_team"
                    ),
                    constraints_applied=["execution_mode:review_only"],
                    knowledge_bundle_id=(
                        context.compiled_package.knowledge_bundle.bundle_id
                        if context.compiled_package
                        else None
                    ),
                    triggering_rule_ids=[match.trigger_id],
                    audit_ref=uuid4(),
                )
                key = action_trace_key(
                    action.action_definition_id,
                    action.target_scope,
                    action.target_id,
                )
                if key in actions_by_key:
                    existing = actions_by_key[key]
                    existing.triggering_rule_ids = sorted(
                        set(existing.triggering_rule_ids + action.triggering_rule_ids)
                    )
                    existing.priority = self._higher_priority(existing.priority, action.priority)
                else:
                    actions_by_key[key] = action

                self._merge_trace(
                    context=context,
                    key=key,
                    action=actions_by_key[key],
                    trigger=trigger,
                    mapping=mapping,
                    match=match,
                )
                sort_metadata[key] = self._best_sort_tuple(
                    sort_metadata.get(key),
                    priority=priority,
                    relationship_type=mapping.relationship_type,
                    target_scope=actions_by_key[key].target_scope,
                )

        return sorted(
            actions_by_key.values(),
            key=lambda action: sort_metadata[
                action_trace_key(action.action_definition_id, action.target_scope, action.target_id)
            ],
        )

    def _resolve_target_id(
        self,
        target_scope: TargetScope,
        match: TriggerMatch,
        context: PolicyExecutionContext,
    ) -> str | None:
        patient_index = {patient.patient_id: patient for patient in context.snapshot.patient_states}
        if target_scope == TargetScope.PATIENT:
            return match.target_id if match.target_scope == "patient" else None
        if target_scope == TargetScope.ROOM:
            patient_state = patient_index.get(match.target_id)
            return (
                patient_state.room_id if patient_state and match.target_scope == "patient" else None
            )
        if target_scope == TargetScope.WARD:
            if match.target_scope == "ward":
                return match.target_id
            patient_state = patient_index.get(match.target_id)
            return (
                patient_state.ward_id if patient_state and match.target_scope == "patient" else None
            )
        if target_scope == TargetScope.HOSPITAL:
            return context.snapshot.hospital_id
        if target_scope == TargetScope.ENTRY_POINT:
            return f"{context.snapshot.hospital_id}:entry-point"
        return None

    def _merge_trace(
        self,
        *,
        context: PolicyExecutionContext,
        key: str,
        action: ProposedAction,
        trigger: PolicyTriggerDefinition,
        mapping: TriggerActionMapping,
        match: TriggerMatch,
    ) -> None:
        trace = context.action_trace_index.setdefault(
            key,
            {
                "runtime_mode": context.runtime_mode,
                "deployment_profile_id": (
                    context.deployment_profile.seasonality_profile_id
                    if context.deployment_profile
                    else None
                ),
                "matched_trigger_ids": [],
                "matched_mapping_ids": [],
                "target_resolution": {
                    "source_scope": match.target_scope,
                    "source_target_id": match.target_id,
                    "resolved_scope": action.target_scope,
                    "resolved_target_id": action.target_id,
                },
                "facts_used": {},
            },
        )
        if trigger.trigger_id not in trace["matched_trigger_ids"]:
            trace["matched_trigger_ids"].append(trigger.trigger_id)
        if mapping.map_id not in trace["matched_mapping_ids"]:
            trace["matched_mapping_ids"].append(mapping.map_id)
        trace["facts_used"][trigger.trigger_id] = match.facts_used

    def _best_sort_tuple(
        self,
        current: tuple[int, int, int] | None,
        *,
        priority: RiskPriority | None,
        relationship_type: str,
        target_scope: TargetScope,
    ) -> tuple[int, int, int]:
        candidate = (
            PRIORITY_ORDER.get(priority or RiskPriority.MEDIUM, 2),
            RELATIONSHIP_ORDER.get((relationship_type or "").lower(), 2),
            TARGET_ORDER.get(target_scope, 5),
        )
        if current is None:
            return candidate
        return min(current, candidate)

    def _priority_from_text(self, value: str | None) -> RiskPriority:
        normalized = (value or "").strip().lower()
        if normalized == "critical":
            return RiskPriority.CRITICAL
        if normalized == "high":
            return RiskPriority.HIGH
        if normalized == "low":
            return RiskPriority.LOW
        return RiskPriority.MEDIUM

    def _higher_priority(
        self,
        left: RiskPriority | None,
        right: RiskPriority | None,
    ) -> RiskPriority | None:
        if left is None:
            return right
        if right is None:
            return left
        return left if PRIORITY_ORDER[left] <= PRIORITY_ORDER[right] else right
