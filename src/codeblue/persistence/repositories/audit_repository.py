from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from codeblue.domain.audit_models import AuditRecord
from codeblue.persistence.orm_models import AuditRecordORM


class AuditRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def store(self, record: AuditRecord) -> AuditRecord:
        self.session.add(
            AuditRecordORM(
                audit_id=str(record.audit_id),
                record_type=record.record_type,
                recorded_at=record.recorded_at,
                actor=record.actor,
                entity_type=record.entity_type,
                entity_id=record.entity_id,
                details=record.details,
                schema_version=record.version_ref.schema_version if record.version_ref else None,
                pathogen_pack_version=(
                    record.version_ref.pathogen_pack_version if record.version_ref else None
                ),
                policy_pack_version=(
                    record.version_ref.policy_pack_version if record.version_ref else None
                ),
                scoring_version=record.version_ref.scoring_version if record.version_ref else None,
                source_event_ids=[
                    str(source_event_id)
                    for source_event_id in (
                        record.provenance.source_event_ids if record.provenance else []
                    )
                ],
                explanation=record.provenance.explanation if record.provenance else None,
            )
        )
        self.session.commit()
        return record

    def get_record(self, audit_id: str) -> AuditRecordORM | None:
        return self.session.get(AuditRecordORM, audit_id)

    def list_all(self) -> list[AuditRecord]:
        records = self.session.scalars(
            select(AuditRecordORM).order_by(AuditRecordORM.recorded_at)
        ).all()
        return [
            AuditRecord.model_validate(
                {
                    "audit_id": record.audit_id,
                    "record_type": record.record_type,
                    "recorded_at": record.recorded_at,
                    "actor": record.actor,
                    "entity_type": record.entity_type,
                    "entity_id": record.entity_id,
                    "details": record.details,
                    "version_ref": (
                        {
                            "schema_version": record.schema_version,
                            "pathogen_pack_version": record.pathogen_pack_version,
                            "policy_pack_version": record.policy_pack_version,
                            "scoring_version": record.scoring_version,
                        }
                        if record.schema_version
                        else None
                    ),
                    "provenance": {
                        "source_event_ids": record.source_event_ids,
                        "explanation": record.explanation,
                    },
                }
            )
            for record in records
        ]
