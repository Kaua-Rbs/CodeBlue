from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from codeblue.domain.governance_models import ReviewDecisionType


class ReviewActionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reviewer_role: str
    decision: ReviewDecisionType
    rationale: str
