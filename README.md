# CodeBlue

CodeBlue is a modular hospital outbreak decision-support platform. It is designed to help hospitals prioritize containment and operational review actions across wards using structured hospital-state data, pathogen-specific outbreak logic, risk scoring, and governed review workflows.

The core product is intentionally pathogen-agnostic. Adapters, pathogen packs, and hospital policy packs are expected to vary, while the canonical schema, temporal state reconstruction, orchestration flow, and audit model remain stable.

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
- SQLAlchemy models and an initial migration for append-only events and review artifacts;
- a temporal state rebuilder for snapshot replay;
- pluggable base interfaces for adapters, pathogen packs, and policy packs;
- a deterministic demo pathogen pack and demo hospital policy pack;
- FastAPI endpoints for health, ingestion, replay, orchestration, risks, actions, review, and explainability; and
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
└── tests/
    ├── unit/
    ├── integration/
    └── fixtures/
```

Implemented documentation:

- [Architecture notes](/home/kauar/CodeBlue/docs/architecture/backend-slice.md)
- [Canonical schema notes](/home/kauar/CodeBlue/docs/schema/canonical-schema.md)
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

## Local Development

Recommended flow:

1. Create the Conda environment from `environment.yml`.
2. Activate the environment.
3. Run the API with `uvicorn codeblue.api.main:app --reload`.
4. Use `docker compose up -d db` or `docker compose up -d` for the standard Postgres-backed setup.

Minimal commands:

```bash
conda env create -f environment.yml
conda activate codeblue
uvicorn codeblue.api.main:app --reload
```

The app defaults to a local SQLite database if `CODEBLUE_DATABASE_URL` is not set. Docker Compose configures PostgreSQL for the standard development path.

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
