# Backend Slice

Status: current
Scope: current Phase 0 backend scaffold and the stable seams it already proves
Last meaningful change: 2026-04-07

Purpose: describe what the current backend implementation already covers, and where it still remains scaffold rather than finished product.

The current implementation is the first backend scaffold for Phase 0. It establishes the stable platform seams from the brief:

- typed canonical event contracts;
- a minimal typed knowledge layer with bundles, rules, and action definitions;
- a knowledge-ingestion and curation scaffold for source evidence tables, helper tabs, trigger sheets, and the new architecture-shaped CSV source package;
- a source compiler that turns the `workbook/` CSV package into runtime deployment profiles, policy triggers, policy actions, trigger-action mappings, and a compiled `KnowledgeBundle`;
- append-only persistence models for events, risk outputs, actions, reviews, and audit records;
- a temporal state rebuilder for snapshot replay;
- pluggable pathogen and policy pack interfaces;
- a deterministic rule evaluator and derived-facts bridge;
- a knowledge-backed demo pathogen pack and demo policy pack;
- a thin FastAPI surface for ingestion, replay, orchestration, review, and explainability;
- a compiled-runtime decision layer that now executes the `workbook/` source package by default for the hackathon demo path;
- direct action priority plus audit-backed trace payloads for the frontend review and trace views.

Raw evidence sources now sit inside the upstream part of the knowledge layer rather than in a separate top-level layer. The current knowledge-ingestion scaffold handles source-sheet classification, schema-family detection, title-row skipping, duplicate-header skipping, helper-sheet extraction, folder-based CSV loading for the new architecture-shaped source package, and compilation of that package into runtime deployment, trigger, action-mapping, and bundle artifacts.

The newer source package under [workbook/](/home/kauar/CodeBlue/workbook) is more architecture-shaped than the earlier source sheets. It now contains explicit influenza-pack, deployment-profile, trigger, action-library, and trigger-action-mapping tables, and the repository now compiles and executes those tables as the default hackathon runtime path. The main remaining gaps are polish-oriented rather than structural: richer supported trigger coverage, better ward/admin facilities, and a more sophisticated risk model.

Implemented flow:

`POST /api/v1/events -> POST /api/v1/runs -> GET /api/v1/state -> GET /api/v1/risk/* -> GET /api/v1/actions -> POST /api/v1/actions/{id}/review`

This is still a scaffold. It proves the boundaries and the end-to-end contract shape, but it is not yet production-ready and does not include real hospital connectors, advanced scoring, or a full review UI.
