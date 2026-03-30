# CodeBlue Development Plan

This document translates the project brief into a practical execution plan for the first development cycle. The immediate objective is not a polished product. It is a working backend slice that proves the platform seams are correct.

## Current Implementation Status

Completed in the current scaffold:

- backend project bootstrap and repository structure;
- Conda environment definition for local development;
- typed domain contracts for canonical events, state, risk, governance, and audit;
- initial persistence models and Alembic migration;
- temporal snapshot reconstruction service;
- adapter, pathogen-pack, and policy-pack interfaces;
- demo influenza-like pathogen pack and demo hospital policy pack;
- minimal FastAPI routes for ingestion, replay, orchestration, review, and explainability; and
- initial tests plus synthetic demo data.

Still to deepen in later iterations:

- richer interval replay semantics and exposure graph logic;
- stronger repository and transaction boundaries;
- more realistic policy constraints and review routing;
- explainability chain linked directly to persisted provenance records;
- seed loaders and command-line tooling; and
- real hospital adapters.

## Target Outcome

Deliver a Phase 0 vertical slice that can:

1. ingest canonical outbreak events;
2. persist them as append-only history;
3. reconstruct temporal hospital state;
4. run a demo pathogen pack and a demo policy pack;
5. emit structured risk outputs and reviewable actions;
6. record review decisions and audit trails; and
7. expose the pipeline through a minimal API.

## Working Assumptions

- The repository will remain a single backend codebase for now.
- PostgreSQL is the system of record.
- The first risk engine can be deterministic or heuristic.
- Synthetic or curated demo data is sufficient for the initial slice.
- A thin API is enough; a full frontend is not needed yet.

## Build Sequence

### Milestone 1: Bootstrap the Backend

Deliverables:

- Conda-managed Python 3.12 environment
- FastAPI app scaffold
- dependency and tooling configuration
- Docker Compose with app and PostgreSQL
- baseline CI checks

Tasks:

- create `pyproject.toml`
- create `environment.yml`
- add FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, pytest, Ruff, mypy, pre-commit
- scaffold `src/codeblue/` and `tests/`
- add `docker-compose.yml`
- add `.env.example`
- add basic CI for lint, types, and tests

Acceptance signal:

- the app starts locally;
- lint/type/test commands run from a clean environment; and
- the repo structure clearly separates domain, application, adapters, packs, persistence, and API.

### Milestone 2: Canonical Schema and Persistence

Deliverables:

- typed Pydantic domain models
- SQLAlchemy persistence models
- initial Alembic migration
- version tracking fields in storage

Tasks:

- define `EventEnvelope` and typed payload models
- define models for risk outputs, proposed actions, review decisions, and audit records
- add append-only event tables
- add tables for assessments, actions, reviews, and audit entries
- persist schema version, pathogen pack version, policy pack version, and scoring version

Acceptance signal:

- ingestion uses the typed canonical models end to end; and
- the database schema supports traceability from event ingestion to reviewed action.

### Milestone 3: Temporal State Reconstruction

Deliverables:

- state rebuilder service
- time-window overlap helpers
- replay-focused unit tests

Tasks:

- reconstruct patient, staff, room, and ward state for a point in time or interval
- implement exposure and co-location overlap utilities
- preserve references to the versions used during replay
- write tests for ordering, overlap, and reconstruction correctness

Acceptance signal:

- a prior operational state can be replayed from stored events and produces expected exposure relationships.

### Milestone 4: Pluggable Packs and Orchestration

Deliverables:

- base interfaces for adapters, pathogen packs, and policy packs
- orchestrator service wired around interfaces
- one demo pathogen pack
- one demo hospital policy pack

Tasks:

- define `DataAdapter`, `PathogenPack`, and `PolicyPack` interfaces
- ensure orchestration depends on abstractions, not concrete demo logic
- implement a demo influenza-like pathogen pack without hard-coding assumptions into the core
- implement a demo hospital governance pack with reviewer roles and constraints

Acceptance signal:

- switching pack instances does not require changing core orchestration code.

### Milestone 5: Risk, Governance, and Audit

Deliverables:

- first-pass risk engine
- policy engine
- review workflow service
- durable audit logging

Tasks:

- emit `RiskAssessment`, `RiskSignal`, and `PriorityAlert`
- convert risk outputs into `ProposedAction`
- apply policy constraints and reviewer routing
- support approve, reject, override, and escalate decisions
- log important system and reviewer actions as audit records

Acceptance signal:

- no action is surfaced outside a governed review state; and
- any generated action can be traced to inputs, versions, and review outcomes.

### Milestone 6: Thin API and Demo Scenario

Deliverables:

- ingestion endpoints
- replay and inspection endpoints
- review endpoints
- synthetic seed/demo loader
- explainability endpoint

Tasks:

- add endpoints for event ingestion
- add endpoints to trigger a run and inspect reconstructed state
- add endpoints to list risks, alerts, and proposed actions
- add endpoint to submit review decisions
- add endpoint to show the chain from source events to action and audit records
- create a small synthetic hospital scenario with plausible outbreak progression

Acceptance signal:

- the seeded scenario runs end to end through the API and yields visible structured outputs and reviewable actions.

## Suggested First Sprint

The current scaffold already covers Milestones 1 and 2 plus the skeleton of Milestones 3 through 6. The next sprint should focus on hardening the domain behavior rather than adding more surface area.

Sprint goals:

- harden replay semantics and interval correctness;
- enrich the risk and governance engines while preserving the current contract boundaries;
- improve explainability and audit linkage; and
- verify the stack in a fully provisioned environment.

Sprint backlog:

1. Add interval-based replay tests for patient moves, staff moves, and room overlap edge cases.
2. Expand the risk engine beyond the current demo heuristics.
3. Persist explainability links from source events to assessments and proposed actions.
4. Add CLI or script-based seed loading for the demo scenario.
5. Add integration tests for ingestion, run, and review flows.
6. Run the stack against installed dependencies and Postgres-backed containers.

## Proposed Task Order for the Repository

1. Create the scaffold and developer tooling.
2. Implement domain contracts before writing application logic.
3. Add persistence and migrations.
4. Add replay logic and tests.
5. Add plugin interfaces and demo packs.
6. Add risk/governance flow.
7. Add API endpoints and seed data.
8. Add explainability and audit inspection endpoints.

## Definition of Done for Phase 0

Phase 0 is complete when all of the following are true:

- canonical event models are in place and used at the ingestion boundary;
- temporal replay works for a prior interval and is covered by tests;
- packs are pluggable and selected without modifying the core workflow;
- governance produces reviewable actions rather than final autonomous commands;
- audit and version tracking exist across the pipeline; and
- a synthetic scenario can be loaded and exercised through the API.

## Anti-Patterns to Avoid

- hard-coding pathogen logic into temporal state or orchestration
- letting hospital-specific adapter fields leak into core models
- generating free-form intervention recommendations directly from the risk layer
- treating auditability as a later concern
- introducing graph databases or microservices before the core model is proven
- optimizing for scale before correctness, modularity, and replayability are validated

## Immediate Next Actions

The next implementation step should be to harden the current scaffold:

1. improve temporal interval reconstruction and overlap tests;
2. connect audit provenance more directly to persisted risk and action records;
3. add a seed loader and end-to-end integration test coverage; and
4. run the stack in an installed environment to validate the runtime path.

The skeleton is now stable enough that future work should refine behavior instead of changing the core layout.
