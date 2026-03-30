from __future__ import annotations

from abc import ABC, abstractmethod

from codeblue.domain.canonical_events import EventEnvelope
from codeblue.domain.risk_models import PriorityAlert, RiskAssessment
from codeblue.domain.state_models import StateSnapshotRef, TimeWindow


class PathogenPack(ABC):
    pack_id: str
    name: str
    version: str

    @abstractmethod
    def assess(
        self,
        events: list[EventEnvelope],
        snapshot: StateSnapshotRef,
        time_window: TimeWindow,
        policy_pack_version: str,
        scoring_version: str,
    ) -> tuple[list[RiskAssessment], list[PriorityAlert]]:
        raise NotImplementedError
