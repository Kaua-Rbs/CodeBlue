from __future__ import annotations

from codeblue.domain.governance_models import ProposedAction
from codeblue.domain.risk_models import RiskAssessment


def build_action_explanation(action: ProposedAction, assessment: RiskAssessment | None) -> str:
    if assessment is None:
        return action.rationale
    return (
        f"{action.action_type} was proposed for {action.target_scope} '{action.target_id}' "
        f"because the risk score was {assessment.score:.2f} with priority '{assessment.priority}'."
    )
