from __future__ import annotations

from codeblue.domain.audit_models import AuditRecord
from codeblue.domain.governance_models import ProposedAction, TargetScope
from codeblue.domain.risk_models import EntityScope, RiskPriority, RiskAssessment
from codeblue.packs.policy.base import PolicyPack


class DemoHospitalPolicyPack(PolicyPack):
    pack_id = "demo_hospital_policy"
    name = "Demo Hospital Policy Pack"
    version = "0.1.0"

    def propose_actions(self, assessments: list[RiskAssessment]) -> list[ProposedAction]:
        actions: list[ProposedAction] = []

        for assessment in assessments:
            if assessment.priority not in {RiskPriority.HIGH, RiskPriority.CRITICAL}:
                continue

            if assessment.entity_scope == EntityScope.ROOM:
                audit = AuditRecord(
                    record_type="proposed_action",
                    actor="policy_engine",
                    entity_type="room",
                    entity_id=assessment.target_id,
                    details={"action_type": "room_isolation_review"},
                )
                actions.append(
                    ProposedAction(
                        risk_assessment_id=assessment.assessment_id,
                        action_type="room_isolation_review",
                        target_scope=TargetScope.ROOM,
                        target_id=assessment.target_id,
                        rationale="High room-level outbreak risk requires IPC review.",
                        required_reviewer_role="ipc_lead",
                        constraints_applied=[
                            "requires_human_review",
                            "no_automatic_orders",
                        ],
                        audit_ref=audit.audit_id,
                    )
                )

            if assessment.entity_scope == EntityScope.WARD:
                audit = AuditRecord(
                    record_type="proposed_action",
                    actor="policy_engine",
                    entity_type="ward",
                    entity_id=assessment.target_id,
                    details={"action_type": "ward_screening_review"},
                )
                actions.append(
                    ProposedAction(
                        risk_assessment_id=assessment.assessment_id,
                        action_type="ward_screening_review",
                        target_scope=TargetScope.WARD,
                        target_id=assessment.target_id,
                        rationale="Ward-level elevated risk requires targeted screening review.",
                        required_reviewer_role="nurse_manager",
                        constraints_applied=[
                            "requires_human_review",
                            "route_to_local_management",
                        ],
                        audit_ref=audit.audit_id,
                    )
                )

        return actions
