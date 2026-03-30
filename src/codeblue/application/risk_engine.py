from __future__ import annotations

from codeblue.domain.canonical_events import EventEnvelope
from codeblue.domain.risk_models import PriorityAlert, RiskAssessment
from codeblue.domain.state_models import StateSnapshotRef
from codeblue.packs.pathogen.base import PathogenPack
from codeblue.packs.policy.base import PolicyPack


class RiskEngine:
    version = "heuristic-risk-engine:0.1.0"

    def assess(
        self,
        events: list[EventEnvelope],
        snapshot: StateSnapshotRef,
        pathogen_pack: PathogenPack,
        policy_pack: PolicyPack,
    ) -> tuple[list[RiskAssessment], list[PriorityAlert]]:
        return pathogen_pack.assess(
            events=events,
            snapshot=snapshot,
            time_window=snapshot.time_window,
            policy_pack_version=policy_pack.version,
            scoring_version=self.version,
        )
