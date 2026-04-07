from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from codeblue.application.policy_engine import PolicyEngine
from codeblue.application.risk_engine import RiskEngine
from codeblue.application.state_rebuilder import TemporalStateRebuilder
from codeblue.domain.audit_models import ProvenanceRef
from codeblue.domain.canonical_events import EventEnvelope
from codeblue.domain.governance_models import ProposedAction
from codeblue.domain.knowledge_runtime_models import PolicyExecutionContext
from codeblue.domain.risk_models import PriorityAlert, RiskAssessment
from codeblue.packs.pathogen.base import PathogenPack
from codeblue.packs.policy.base import PolicyPack
from codeblue.persistence.repositories.audit_repository import AuditRepository
from codeblue.persistence.repositories.governance_repository import GovernanceRepository
from codeblue.persistence.repositories.risk_repository import RiskRepository
from codeblue.services.audit import AuditService
from codeblue.services.versioning import build_version_ref


@dataclass
class OrchestrationResult:
    snapshot_at: str
    assessments: list[RiskAssessment]
    alerts: list[PriorityAlert]
    actions: list[ProposedAction]
    runtime_mode: str
    knowledge_bundle_id: str | None = None
    deployment_profile_id: str | None = None
    matched_trigger_count: int = 0


class OutbreakOrchestrator:
    def __init__(
        self,
        session: Session,
        pathogen_pack: PathogenPack,
        policy_pack: PolicyPack,
        policy_context_builder: object | None = None,
    ) -> None:
        self.session = session
        self.pathogen_pack = pathogen_pack
        self.policy_pack = policy_pack
        self.policy_context_builder = policy_context_builder
        self.state_rebuilder = TemporalStateRebuilder()
        self.risk_engine = RiskEngine()
        self.policy_engine = PolicyEngine()
        self.audit_service = AuditService()
        self.risk_repository = RiskRepository(session)
        self.governance_repository = GovernanceRepository(session)
        self.audit_repository = AuditRepository(session)

    def run(self, events: list[EventEnvelope]) -> OrchestrationResult:
        if not events:
            raise ValueError("At least one event is required for orchestration.")

        snapshot_at = max(event.occurred_at for event in events)
        snapshot = self.state_rebuilder.rebuild_snapshot(events, snapshot_at)
        policy_context = self._build_policy_context(events, snapshot)
        assessments, alerts = self.risk_engine.assess(
            events=events,
            snapshot=snapshot,
            pathogen_pack=self.pathogen_pack,
            policy_pack=self.policy_pack,
        )
        version_ref = build_version_ref(
            schema_version=events[0].schema_version,
            pathogen_pack=self.pathogen_pack,
            policy_pack=self.policy_pack,
            scoring_version=self.risk_engine.version,
        )

        actions = self.policy_engine.propose_actions(assessments, self.policy_pack, policy_context)

        self.governance_repository.clear_actions_and_reviews()
        self.risk_repository.clear_assessments_and_alerts()
        self.risk_repository.store_assessments(assessments)
        self.risk_repository.store_alerts(alerts)
        for action in actions:
            trace = self._trace_for_action(action, policy_context)
            audit_record = self.audit_service.create_record(
                record_type="proposed_action",
                actor="policy_engine",
                entity_type=action.target_scope,
                entity_id=action.target_id,
                details={
                    "action_type": action.action_type,
                    "status": action.status,
                    "action_definition_id": action.action_definition_id,
                    "knowledge_bundle_id": action.knowledge_bundle_id,
                    "triggering_rule_ids": action.triggering_rule_ids,
                    "runtime_mode": policy_context.runtime_mode,
                    "trace": trace,
                },
                version_ref=version_ref,
                provenance=ProvenanceRef(
                    source_event_ids=snapshot.source_event_ids,
                    explanation=action.rationale,
                ),
            )
            action.audit_ref = audit_record.audit_id
            self.audit_repository.store(audit_record)

        self.governance_repository.store_actions(actions)

        return OrchestrationResult(
            snapshot_at=snapshot.at.isoformat(),
            assessments=assessments,
            alerts=alerts,
            actions=actions,
            runtime_mode=policy_context.runtime_mode,
            knowledge_bundle_id=(
                policy_context.compiled_package.knowledge_bundle.bundle_id
                if policy_context.compiled_package
                else (actions[0].knowledge_bundle_id if actions else None)
            ),
            deployment_profile_id=(
                policy_context.deployment_profile.seasonality_profile_id
                if policy_context.deployment_profile
                else None
            ),
            matched_trigger_count=len(policy_context.matched_triggers),
        )

    def _build_policy_context(
        self,
        events: list[EventEnvelope],
        snapshot: object,
    ) -> PolicyExecutionContext:
        if self.policy_context_builder is not None:
            return self.policy_context_builder.build(events, snapshot)
        return PolicyExecutionContext(
            runtime_mode="legacy",
            events=events,
            snapshot=snapshot,
            hospital_id=snapshot.hospital_id,
        )

    def _trace_for_action(
        self,
        action: ProposedAction,
        context: PolicyExecutionContext,
    ) -> dict[str, object] | None:
        key = f"{action.action_definition_id or 'unknown'}|{action.target_scope}|{action.target_id}"
        return context.action_trace_index.get(key)
