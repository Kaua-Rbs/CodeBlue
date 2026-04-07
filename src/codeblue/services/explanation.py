from __future__ import annotations

from typing import Any

from codeblue.domain.governance_models import ProposedAction
from codeblue.domain.risk_models import RiskAssessment


def build_action_explanation(
    action: ProposedAction,
    assessment: RiskAssessment | None,
    trace: dict[str, Any] | None = None,
) -> str:
    if trace and trace.get("matched_trigger_ids"):
        trigger_ids = ", ".join(trace["matched_trigger_ids"])
        return (
            f"{action.action_type} was proposed for {action.target_scope} '{action.target_id}' "
            f"because compiled triggers matched: {trigger_ids}."
        )
    if assessment is None:
        return action.rationale
    return (
        f"{action.action_type} was proposed for {action.target_scope} '{action.target_id}' "
        f"because the risk score was {assessment.score:.2f} with priority '{assessment.priority}'."
    )
