# CodeBlue

CodeBlue is a modular hospital outbreak decision-support platform. It is designed to help hospitals prioritize containment and operational review actions across wards using structured hospital-state data, pathogen-specific outbreak logic, risk scoring, and governed review workflows.

The core product is intentionally pathogen-agnostic. Adapters, pathogen packs, and hospital policy packs are expected to vary, while the canonical schema, temporal state reconstruction, orchestration flow, and audit model remain stable.

In the current repository, the first source knowledge package happens to be a live multi-tab spreadsheet. It is handled as part of the knowledge ingestion and curation submodule inside the broader knowledge layer before translation into executable knowledge bundles.

## Product Goals

- Ingest outbreak-relevant hospital events into a canonical internal schema.
- Reconstruct a time-indexed operational hospital state from append-only history.
- Interpret that state with pluggable pathogen packs.
- Produce structured risk outputs such as scores, priorities, and alerts.
- Convert those outputs into reviewable actions through pluggable policy/governance packs.
- Preserve auditability, traceability, and versioning across the full pipeline.

## Core Principles

- Stable core, variable packs: the reusable platform should not be rewritten for each pathogen or hospital.
- Time matters: the system must reconstruct what was known, where, and when.
- Structured AI boundary: the risk layer emits scores, rankings, and alerts, not unrestricted recommendations.
- Governance is mandatory: surfaced actions must be permissible, reviewable, and auditable.
- Demo without lock-in: the first demo may use one example pathogen pack, but the codebase must remain generic.

## High-Level Architecture

End-to-end flow:

`hospital data -> adapters -> canonical schema -> temporal hospital state -> pathogen pack -> risk engine -> policy/governance pack -> reviewable actions -> audit trail -> API/UI`

Stable platform modules:

- Canonical schema
- Temporal hospital state reconstruction
- Risk/output contracts
- Orchestration flow
- Audit and version tracking
- API shell

Variable modules:

- Hospital data adapters
- Pathogen packs
- Hospital policy/governance packs
- Presentation layer details

## Recommended Stack

- Python 3.12
- FastAPI + Pydantic v2
- PostgreSQL
- SQLAlchemy 2.0 + Alembic
- NetworkX for initial graph/state reasoning
- Conda for local environment management
- Ruff, mypy, pytest, pre-commit
- Docker Compose for local app + database setup

## Phase 0 Scope

The first milestone is one end-to-end backend slice:

1. Ingest synthetic or curated outbreak events.
2. Map them into the canonical schema.
3. Reconstruct temporal hospital state for a time instant or interval.
4. Load one demo pathogen pack and one demo hospital policy pack.
5. Generate structured risk outputs.
6. Filter them into reviewable actions.
7. Persist audit records and version references.
8. Expose the flow through a thin API.

Out of scope for Phase 0:

- Real hospital connectors beyond mock adapters
- Trained ML pipelines
- Microservices or message buses
- Heavy simulation or digital twin features
- Polished production UI

## Implemented In This Repository

The repository now includes the first backend scaffold for Phase 0:

- project bootstrap with `pyproject.toml`, Docker, Alembic, CI, and pre-commit;
- Conda environment definition in `environment.yml`;
- typed domain contracts for canonical events, state, risk, governance, and audit;
- typed knowledge-ingestion contracts for both the earlier multi-sheet source format and the new architecture-shaped CSV source package;
- a source compiler that turns the `workbook/` CSV package into a compiled bundle plus deployment, trigger, action, and mapping runtime objects;
- a compiled default runtime path for `/api/v1/runs` that evaluates deployment seasonality, symptomatic arrival, inpatient influenza, and ward-cluster triggers;
- SQLAlchemy models and an initial migration for append-only events and review artifacts;
- a temporal state rebuilder for snapshot replay;
- pluggable base interfaces for adapters, pathogen packs, and policy packs;
- a deterministic demo pathogen pack and demo hospital policy pack;
- a knowledge-source parser scaffold for evidence tabs, library tabs, trigger notes, abbreviation sheets, and the `workbook/` CSV package;
- FastAPI endpoints for health, ingestion, replay, orchestration, risks, actions, review, and explainability; and
- structured explainability trace payloads backed by audit records;
- a first real frontend scaffold under `frontend/` using React, TypeScript, Vite, React Router, TanStack Query, Zustand, and token-based CSS;
- seed/demo data plus initial tests for event validation and replay logic.

## Initial Domain Contracts

Expected canonical event categories:

- Patient location events
- Staff assignment and movement events
- Lab confirmation events
- Suspected case events
- Ward and room metadata events
- Adjacency and containment events
- Intervention and review events
- Audit and version reference records

Expected core output categories:

- `RiskAssessment`
- `RiskSignal`
- `PriorityAlert`
- `ProposedAction`
- `ActionReviewRequest`
- `ReviewDecision`
- `AuditRecord`
- `VersionRef`
- `ProvenanceRef`

## Planned Repository Structure

```text
codeblue/
├── README.md
├── pyproject.toml
├── docker-compose.yml
├── alembic.ini
├── .env.example
├── migrations/
├── docs/
│   ├── architecture/
│   ├── schema/
│   ├── demo/
│   └── development-plan.md
├── seed/
│   ├── synthetic_events/
│   └── demo_scenarios/
├── src/codeblue/
│   ├── api/
│   ├── domain/
│   ├── application/
│   ├── packs/
│   ├── adapters/
│   ├── persistence/
│   ├── services/
│   └── settings.py
├── frontend/
│   ├── src/
│   └── package.json
└── tests/
    ├── unit/
    ├── integration/
    └── fixtures/
```

Implemented documentation:

- [Architecture notes](/home/kauar/CodeBlue/docs/architecture/backend-slice.md)
- [Project owner brief](/home/kauar/CodeBlue/docs/architecture/project-owner-brief.md)
- [Architecture decisions](/home/kauar/CodeBlue/docs/architecture/decisions/README.md)
- [Documentation guidelines](/home/kauar/CodeBlue/docs/architecture/documentation-guidelines.md)
- [Frontend stack justifications](/home/kauar/CodeBlue/docs/architecture/frontend-stack-justifications.md)
- [Frontend UX plan](/home/kauar/CodeBlue/docs/architecture/frontend-ux-plan.md)
- [Frontend screen specification](/home/kauar/CodeBlue/docs/architecture/frontend-screen-spec.md)
- [High-level architecture](/home/kauar/CodeBlue/docs/architecture/high-level-architecture.md)
- [Current architecture diagram](/home/kauar/CodeBlue/docs/architecture/current-architecture-diagram.md)
- [Layer contracts](/home/kauar/CodeBlue/docs/architecture/layer-contracts.md)
- [Overall architecture layers](/home/kauar/CodeBlue/docs/architecture/overall-architecture-layers.md)
- [HSIL RISCOS mapping](/home/kauar/CodeBlue/docs/architecture/hsil-riscos-mapping.md)
- [Knowledge source compiler plan](/home/kauar/CodeBlue/docs/architecture/knowledge-source-compiler-plan.md)
- [Knowledge roadmap](/home/kauar/CodeBlue/docs/architecture/knowledge-roadmap.md)
- [Knowledge schema design](/home/kauar/CodeBlue/docs/architecture/knowledge-schema-design.md)
- [Stack choice justifications](/home/kauar/CodeBlue/docs/architecture/stack-justifications.md)
- [Knowledge ingestion and curation](/home/kauar/CodeBlue/docs/architecture/knowledge-ingestion-and-curation.md)
- [Canonical schema notes](/home/kauar/CodeBlue/docs/schema/canonical-schema.md)
- [Frontend demo prototype note](/home/kauar/CodeBlue/docs/demo/frontend-prototype.md)
- [Phase 0 API walkthrough](/home/kauar/CodeBlue/docs/demo/phase0-api.md)
- [Development plan](/home/kauar/CodeBlue/docs/development-plan.md)

## Development Priorities

Build the invariant backbone first:

1. Project bootstrap and quality tooling
2. Canonical schema and persistence
3. Temporal replay and overlap logic
4. Plugin interfaces for adapters, pathogen packs, and policy packs
5. Risk, governance, and audit contracts
6. Thin API and synthetic demo pipeline

The detailed execution plan lives in [docs/development-plan.md](/home/kauar/CodeBlue/docs/development-plan.md).

## API Surface

Current routes:

- `GET /health`
- `POST /api/v1/events`
- `GET /api/v1/events`
- `GET /api/v1/state`
- `POST /api/v1/runs`
- `GET /api/v1/risk/assessments`
- `GET /api/v1/risk/alerts`
- `GET /api/v1/actions`
- `POST /api/v1/actions/{action_id}/review`
- `GET /api/v1/explainability/actions/{action_id}`

`POST /api/v1/runs` now returns runtime metadata including the active runtime mode, compiled knowledge bundle id, deployment profile id, and matched trigger count. `GET /api/v1/explainability/actions/{action_id}` now returns both a narrative explanation and a structured trace payload for the frontend trace drawer.

## Local Development

Recommended flow:

1. Create the Conda environment from `environment.yml`.
2. Activate the environment.
3. Run the API with `uvicorn codeblue.api.main:app --reload`.
4. Install and run the frontend from `frontend/`.
5. Use `docker compose up -d db` or `docker compose up -d` for the standard Postgres-backed setup.

Minimal commands:

```bash
conda env create -f environment.yml
conda activate codeblue
uvicorn codeblue.api.main:app --reload
cd frontend
npm install
npm run dev
```

The app defaults to a local SQLite database if `CODEBLUE_DATABASE_URL` is not set. Docker Compose configures PostgreSQL for the standard development path.

The frontend runs on Vite's default dev server and proxies `/health` and `/api/*` to the FastAPI backend on `127.0.0.1:8000`.

Conda is the recommended local workflow. The container build remains `pip`-based so Docker stays lightweight and self-contained.

## Definition of Success for the First Slice

Phase 0 is successful when:

- canonical events are typed and persisted;
- historical state can be replayed for a prior interval;
- pathogen and policy packs are swappable without core changes;
- actions are reviewable instead of emitted as final commands;
- generated outputs can be traced to source events, versions, and review outcomes; and
- a seeded synthetic scenario produces visible risk outputs and governed actions through the API.

## Current Status

This repository now contains the first implemented Phase 0 scaffold. The next development step is to deepen the temporal replay, risk logic, and governance workflow rather than reworking the project skeleton.
