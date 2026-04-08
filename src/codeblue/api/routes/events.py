from __future__ import annotations

from fastapi import APIRouter

from codeblue.api.dependencies import SessionDependency
from codeblue.api.schemas.events import IngestEventsRequest, IngestEventsResponse
from codeblue.domain.canonical_events import EventEnvelope
from codeblue.persistence.repositories.event_repository import EventRepository

router = APIRouter(prefix="/events", tags=["events"])


@router.post("", response_model=IngestEventsResponse)
def ingest_events(
    request: IngestEventsRequest,
    session: SessionDependency,
) -> IngestEventsResponse:
    repository = EventRepository(session)
    stored_events = repository.add_many(request.events)
    return IngestEventsResponse(
        ingested_count=len(stored_events),
        event_ids=[str(event.event_id) for event in stored_events],
    )


@router.get("", response_model=list[EventEnvelope])
def list_events(session: SessionDependency) -> list[EventEnvelope]:
    repository = EventRepository(session)
    return repository.list_all()
