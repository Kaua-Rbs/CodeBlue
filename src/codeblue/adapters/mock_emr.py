from __future__ import annotations

from typing import Any

from codeblue.adapters.base import DataAdapter
from codeblue.domain.canonical_events import EventEnvelope


class MockEmrAdapter(DataAdapter):
    adapter_name = "mock_emr"

    def map_events(self, raw_records: list[dict[str, Any]]) -> list[EventEnvelope]:
        return [EventEnvelope.model_validate(record) for record in raw_records]
