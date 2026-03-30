from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from codeblue.domain.canonical_events import EventEnvelope
from codeblue.persistence.orm_models import EventRecord


class EventRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add_many(self, events: list[EventEnvelope]) -> list[EventEnvelope]:
        for event in events:
            record = EventRecord(
                event_id=str(event.event_id),
                event_type=event.event_type,
                hospital_id=event.hospital_id,
                source_system=event.source_system,
                schema_version=event.schema_version,
                occurred_at=event.occurred_at,
                recorded_at=event.recorded_at,
                payload=event.payload.model_dump(mode="json"),
            )
            self.session.add(record)
        self.session.commit()
        return events

    def list_all(self) -> list[EventEnvelope]:
        records = self.session.scalars(select(EventRecord).order_by(EventRecord.occurred_at)).all()
        return [
            EventEnvelope.model_validate(
                {
                    "event_id": record.event_id,
                    "event_type": record.event_type,
                    "occurred_at": record.occurred_at,
                    "recorded_at": record.recorded_at,
                    "source_system": record.source_system,
                    "hospital_id": record.hospital_id,
                    "payload": record.payload,
                    "schema_version": record.schema_version,
                }
            )
            for record in records
        ]
