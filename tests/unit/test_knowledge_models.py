from __future__ import annotations

import pytest

from codeblue.domain.knowledge_models import RuleCondition


def test_rule_condition_rejects_multiple_shapes() -> None:
    with pytest.raises(ValueError):
        RuleCondition.model_validate(
            {
                "all": [{"fact": "lab.confirmed_pathogen", "op": "eq", "value": "influenza"}],
                "fact": "encounter.hours_since_admission",
                "op": "gt",
                "value": 96,
            }
        )


def test_rule_condition_rejects_exists_with_value() -> None:
    with pytest.raises(ValueError):
        RuleCondition.model_validate(
            {"fact": "lab.confirmed_pathogen", "op": "exists", "value": "influenza"}
        )
