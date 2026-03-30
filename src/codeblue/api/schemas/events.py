from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from codeblue.domain.canonical_events import EventEnvelope


class IngestEventsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    events: list[EventEnvelope] = Field(min_length=1)


class IngestEventsResponse(BaseModel):
    ingested_count: int
    event_ids: list[str]
