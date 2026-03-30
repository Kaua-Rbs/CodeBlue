from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from codeblue.domain.canonical_events import EventEnvelope


class DataAdapter(ABC):
    adapter_name: str

    @abstractmethod
    def map_events(self, raw_records: list[dict[str, Any]]) -> list[EventEnvelope]:
        raise NotImplementedError
