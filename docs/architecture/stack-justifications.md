# Stack Choice Justifications

Status: current
Scope: rationale for the current Phase 0 technology stack and the repository's main stack-level tradeoffs
Last meaningful change: 2026-04-05

Purpose: record why the current stack was chosen, what role each component plays, and where the repository intentionally deviates from the original brief.

This document captures the reasoning behind the current Phase 0 stack choices for CodeBlue. It is based on the project brief, but it is more explicit than the PDF about why each tool was selected and what role it plays in the system.

## Relationship To The Project Brief

The development brief already recommends most of this stack directly:

- `Python 3.12`
- `FastAPI + Pydantic v2`
- `PostgreSQL`
- `SQLAlchemy 2.0 + Alembic`
- `NetworkX initially`
- `uv, Ruff, mypy, pytest, pre-commit`
- `Docker Compose`

The brief also gives short reasons for many of those choices, especially around:

- typed backend services;
- graph-like operational reasoning;
- future ML and analytics work;
- strong API and contract boundaries;
- transactional persistence;
- selective `JSONB` usage;
- graph logic in application code before adopting a graph database; and
- fast setup with strong linting, typing, and test discipline.

What the PDF does not do is spell out the full justification for each tool in the same level of detail as the rationale below. This file fills that gap.

## Stack Rationale

### Python 3.12

Python is the right default because CodeBlue sits at the intersection of:

- typed domain modeling;
- API-oriented backend development;
- validation and serialization;
- graph reasoning; and
- likely future ML and analytics work.

Python is also the ecosystem sweet spot for the rest of the chosen stack: FastAPI, Pydantic, SQLAlchemy, NetworkX, mypy, and pytest. Python 3.12 is a practical baseline because it gives modern typing support and strong current library compatibility without starting a new codebase on an older runtime.

### FastAPI

FastAPI is a strong fit because the first milestone is a typed backend pipeline exposed through clean APIs. CodeBlue needs routes for canonical event ingestion, replay/state inspection, orchestration runs, risk output retrieval, action review, and explainability. FastAPI works naturally with Python type hints and gives OpenAPI documentation immediately, which is useful for a backend-first project whose first UI is effectively the API surface itself.

### Pydantic v2

Pydantic is the foundation for the canonical internal schema. CodeBlue depends on explicit, validated domain objects at every boundary:

- canonical event envelopes;
- typed event payloads;
- temporal state objects;
- structured risk outputs;
- governance objects; and
- audit/versioning records.

Pydantic v2 is a good fit because it keeps validation and serialization close to the type definitions themselves. That is important in a system where portability depends on not letting hospital-specific or pack-specific assumptions leak into the core contracts.

### SQLAlchemy 2.0

SQLAlchemy is appropriate because CodeBlue needs a durable relational persistence layer without forcing the implementation into either a pure ORM-only style or raw SQL everywhere. Different parts of the system have different shapes:

- append-only event storage;
- review and audit entities;
- structured risk output records; and
- queries that may become more temporal or investigative over time.

SQLAlchemy 2.0 keeps the persistence layer explicit and flexible, which matters in an architecture that is still stabilizing.

### Alembic

Alembic is the natural migration tool because schema evolution is guaranteed early in this project. The canonical schema, replay model, governance records, and audit layer will all change as the platform sharpens. Using migrations from day one is safer than treating the schema as temporary and patching it manually later.

### PostgreSQL

PostgreSQL is a strong fit because CodeBlue needs both relational discipline and selective flexibility. It is the right source of truth for:

- events;
- risk outputs;
- proposed actions;
- review decisions; and
- audit records.

Its relational model fits the transactional core, while `JSONB` is useful for payload fragments, evidence lists, and versioned rule metadata where strict columns would be too rigid too early. PostgreSQL also keeps the door open for more sophisticated temporal querying later.

### NetworkX

NetworkX is the right first implementation tool for graph-shaped reasoning because CodeBlue needs to reason about:

- adjacency between rooms and wards;
- patient and staff movement;
- overlap and exposure windows;
- bridge-risk paths; and
- operational relationships that are graph-like but not yet database-scale.

It gives the project graph logic in application code without prematurely introducing a graph database. That matches the brief’s architectural warning against adding graph-specific infrastructure before the core model has been proven.

### uv

`uv` was originally recommended because it reduces Python project-management friction in an early-stage codebase. For a repo that needs quick onboarding, repeatable dependency management, and a tight inner loop, a fast unified tool is attractive.

That said, the current repository has been adjusted to prefer Conda for local environment management. If the team stays Conda-first, `uv` should no longer be treated as the primary environment tool in practice, even though it appeared in the original brief.

### Ruff

Ruff is a good fit because it keeps the codebase strict without multiplying tooling overhead. CodeBlue’s value depends heavily on clean domain boundaries and stable contracts, so fast linting and formatting help keep the repo disciplined while the core abstractions are still being established.

### mypy

mypy matters because the architecture is built around interfaces and contracts:

- adapters;
- pathogen packs;
- policy packs;
- structured risk outputs;
- review workflows; and
- audit/versioning objects.

Static checking helps catch boundary mistakes before runtime, which is especially valuable in a platform whose main design challenge is preserving modularity and correctness between layers.

### pytest

pytest is a strong fit because the first backend slice should be validated through small, clear invariants:

- event validation;
- replay correctness;
- overlap logic;
- pack behavior;
- governance state transitions; and
- audit creation.

Its fixture model is especially useful for reusable synthetic hospital scenarios, which the brief explicitly treats as sufficient for the early demo.

### Docker Compose

Docker Compose is useful because even the first meaningful local version of CodeBlue benefits from a reproducible multi-service setup:

- API service;
- PostgreSQL database; and
- any future local support services.

That makes onboarding easier and keeps development closer to a realistic deployment shape without forcing an early move into distributed infrastructure.

## Practical Summary

The brief already contains the stack recommendation and a substantial part of the reasoning. What it does not contain is this fully expanded justification layer for each component. This file should be treated as the explicit decision record for why the Phase 0 stack exists in its current form.

One important note for this repository: the original brief recommended `uv`, but the repository currently documents Conda as the local environment workflow. That is now a project-level deviation from the original recommendation and should be revisited if the team wants strict alignment with the brief.
