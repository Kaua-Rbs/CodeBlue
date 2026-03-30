# Backend Slice

The current implementation is the first backend scaffold for Phase 0. It establishes the stable platform seams from the brief:

- typed canonical event contracts;
- append-only persistence models for events, risk outputs, actions, reviews, and audit records;
- a temporal state rebuilder for snapshot replay;
- pluggable pathogen and policy pack interfaces;
- a deterministic demo pathogen pack and demo policy pack;
- a thin FastAPI surface for ingestion, replay, orchestration, review, and explainability.

Implemented flow:

`POST /api/v1/events -> POST /api/v1/runs -> GET /api/v1/state -> GET /api/v1/risk/* -> GET /api/v1/actions -> POST /api/v1/actions/{id}/review`

This is still a scaffold. It proves the boundaries and the end-to-end contract shape, but it is not yet production-ready and does not include real hospital connectors, advanced scoring, or a full review UI.
