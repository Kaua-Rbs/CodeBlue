# Current Architecture Diagram

Status: current
Scope: presentation of the current implemented backend flow and current knowledge-layer placement
Last meaningful change: 2026-04-05

Purpose: capture the architecture as it exists in the current Phase 0 scaffold, rather than the full intended end-state.

This note captures the current CodeBlue architecture as it exists in the Phase 0 backend scaffold.

## Runtime Pipeline

```mermaid
flowchart LR
    A[Hospital Data] --> B[Adapters]
    B --> C[Canonical Schema]
    C --> D[Event Persistence]
    C --> E[Temporal State Rebuilder]
    E --> F[Derived Facts Bridge]
    F --> G[Pathogen Pack]
    G --> H[Risk Engine]
    H --> I[Policy / Governance Pack]
    I --> J[Reviewable Actions]
    J --> K[Action Review]
    H --> L[Audit and Version Tracking]
    I --> L
    J --> L
    D --> M[FastAPI]
    E --> M
    H --> M
    J --> M
    K --> M
```

## Knowledge Layer Placement

```mermaid
flowchart TB
    KS[Knowledge Sources]
    KI[Knowledge Ingestion and Curation]
    KB[Knowledge Bundle]

    KS --> KI
    KI --> KB
    KB --> SD[Source Documents]
    KB --> PP[Pathogen Packs]
    KB --> GP[Policy Packs]
    KB --> WF[Workflow / Review Packs]
    KB --> RA[Rule Artifacts]
    KB --> AC[Action Catalog]
    KB --> EV[Evidence Statements]
    KB --> TB[Terminology Bindings]
    KB --> TC[Knowledge Test Cases]

    SD --> RA
    EV --> RA
    AC --> GP
    AC --> WF

    RA --> RE[Rule Evaluator]
    TB --> FB[Facts Bridge]
    FB --> RE
    RE --> PP
    RE --> GP
    RE --> WF
```

## Stable vs Variable Layers

Stable platform layers:

- Canonical schema
- Temporal state reconstruction
- Knowledge ingestion and curation
- Derived facts and rule evaluation
- Risk/output contracts
- Orchestration flow
- Audit and version tracking
- API shell

Variable layers:

- Hospital data adapters
- Pathogen packs
- Policy/governance packs
- Review workflow packs
- Knowledge bundle contents
- Presentation layer
