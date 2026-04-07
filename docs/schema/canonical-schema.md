# Canonical Schema

Status: current
Scope: current canonical domain-model split and event-envelope invariants
Last meaningful change: 2026-04-05

Purpose: summarize the stable canonical contracts that form the shared internal language of the system.

The current canonical model layer lives in `src/codeblue/domain/` and is intentionally split by concern:

- `canonical_events.py`: outbreak-relevant ingest contracts
- `state_models.py`: replay and snapshot models
- `risk_models.py`: structured AI/risk outputs
- `governance_models.py`: reviewable action contracts
- `audit_models.py`: versioning and traceability records

Implemented event payload types:

- `PatientLocationEvent`
- `StaffAssignmentEvent`
- `LabConfirmationEvent`
- `SuspectedCaseEvent`
- `WardMetadataEvent`
- `RoomMetadataEvent`
- `AdjacencyEdgeEvent`
- `InterventionEvent`

Each event enters through `EventEnvelope`, which carries:

- globally unique event id
- event type
- occurred and recorded timestamps
- source system
- hospital id
- typed payload
- schema version

The envelope validates that the declared event type matches the payload event type, which prevents adapters from leaking ambiguous or malformed contracts into the core.
