from __future__ import annotations

from abc import ABC, abstractmethod

from codeblue.domain.governance_models import ProposedAction
from codeblue.domain.knowledge_runtime_models import PolicyExecutionContext
from codeblue.domain.risk_models import RiskAssessment


class PolicyPack(ABC):
    pack_id: str
    name: str
    version: str

    @abstractmethod
    def propose_actions(
        self,
        assessments: list[RiskAssessment],
        context: PolicyExecutionContext | None = None,
    ) -> list[ProposedAction]:
        raise NotImplementedError
