from __future__ import annotations

from codeblue.domain.canonical_events import EventEnvelope
from codeblue.domain.risk_models import PriorityAlert, RiskAssessment
from codeblue.domain.state_models import StateSnapshotRef, TimeWindow
from codeblue.packs.pathogen.base import PathogenPack


class CompiledWorkbookPathogenPack(PathogenPack):
    pack_id = "pathogen_influenza_compiled_workbook_v1"
    name = "Compiled Workbook Influenza Pathogen Pack"
    version = "1.0.0"

    def assess(
        self,
        events: list[EventEnvelope],
        snapshot: StateSnapshotRef,
        time_window: TimeWindow,
        policy_pack_version: str,
        scoring_version: str,
    ) -> tuple[list[RiskAssessment], list[PriorityAlert]]:
        return [], []
