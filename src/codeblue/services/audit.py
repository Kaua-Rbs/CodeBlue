from __future__ import annotations

from codeblue.domain.audit_models import AuditRecord, ProvenanceRef, VersionRef


class AuditService:
    def create_record(
        self,
        record_type: str,
        actor: str,
        entity_type: str,
        entity_id: str,
        details: dict[str, object],
        version_ref: VersionRef | None = None,
        provenance: ProvenanceRef | None = None,
    ) -> AuditRecord:
        return AuditRecord(
            record_type=record_type,
            actor=actor,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            version_ref=version_ref,
            provenance=provenance,
        )
