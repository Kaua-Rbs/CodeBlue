from __future__ import annotations

from codeblue.domain.governance_models import ProposedAction
from codeblue.domain.risk_models import RiskAssessment
from codeblue.packs.policy.base import PolicyPack


class PolicyEngine:
    def propose_actions(
        self,
        assessments: list[RiskAssessment],
        policy_pack: PolicyPack,
    ) -> list[ProposedAction]:
        return policy_pack.propose_actions(assessments)
