from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from codeblue.application.state_rebuilder import TemporalStateRebuilder
from codeblue.domain.state_models import StateSnapshotRef
from codeblue.persistence.db import get_session
from codeblue.persistence.repositories.event_repository import EventRepository

router = APIRouter(prefix="/state", tags=["state"])


@router.get("", response_model=StateSnapshotRef)
def get_state(
    at: datetime | None = Query(default=None),
    session: Session = Depends(get_session),
) -> StateSnapshotRef:
    repository = EventRepository(session)
    events = repository.list_all()
    if not events:
        raise HTTPException(status_code=400, detail="No events are available for state reconstruction.")
    rebuilder = TemporalStateRebuilder()
    target_time = at or max(event.occurred_at for event in events)
    return rebuilder.rebuild_snapshot(events, target_time)
