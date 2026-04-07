# Overall Architecture Layers

Status: current
Scope: layer-by-layer architecture view of the full CodeBlue system
Last meaningful change: 2026-04-05

Purpose: show CodeBlue as a layered architecture instead of only a request pipeline, with the major responsibilities separated by layer.

This diagram shows CodeBlue as a layered architecture rather than only as a request pipeline.

## Layered View

```mermaid
flowchart TB
    subgraph L1[Layer 1: External Sources]
        A1[Hospital Operational Data]
        A2[Policies and Guidelines]
        A3[Literature and Evidence]
        A4[User Review Decisions]
    end

    subgraph L2[Layer 2: Operational Ingestion]
        B1[Adapters]
        B2[Operational Mapping]
    end

    subgraph L3[Layer 3: Canonical Core]
        C1[Canonical Event Schema]
        C2[Canonical Domain Models]
        C3[Append-Only Event Log]
    end

    subgraph L4[Layer 4: State and Facts]
        D1[Temporal State Rebuilder]
        D2[Exposure and Overlap Logic]
        D3[Derived Facts Bridge]
    end

    subgraph L5[Layer 5: Knowledge Layer]
        E1[Knowledge Sources]
        E2[Knowledge Ingestion and Curation]
        E3[Knowledge Bundle]
        E4[Source Documents]
        E5[Rule Artifacts and DSL]
        E6[Action Catalog]
        E7[Evidence Statements]
        E8[Knowledge Test Cases]
    end

    subgraph L6[Layer 6: Reasoning and Orchestration]
        F1[Rule Evaluator]
        F2[Pathogen Packs]
        F3[Risk Engine]
        F4[Policy and Governance Packs]
        F5[Review Workflow Logic]
        F6[Orchestrator]
    end

    subgraph L7[Layer 7: Outputs and Control]
        G1[Risk Assessments]
        G2[Priority Alerts]
        G3[Reviewable Actions]
        G4[Review Decisions]
    end

    subgraph L8[Layer 8: Audit and Persistence]
        H1[Version Tracking]
        H2[Audit Records]
        H3[Action and Review Persistence]
        H4[Knowledge Persistence]
    end

    subgraph L9[Layer 9: Delivery]
        I1[FastAPI]
        I2[Explainability Endpoints]
        I3[Future UI]
    end

    A1 --> B1
    A4 --> G4
    A2 --> E1
    A3 --> E1

    B1 --> B2
    B2 --> C1

    C1 --> C2
    C2 --> C3
    C3 --> D1
    D1 --> D2
    D2 --> D3

    E1 --> E2
    E2 --> E3
    E2 --> E4
    E2 --> E7
    E3 --> E4
    E3 --> E5
    E3 --> E6
    E3 --> E7
    E3 --> E8

    D3 --> F1
    E5 --> F1
    E6 --> F4
    E7 --> F2
    F1 --> F2
    F2 --> F3
    F3 --> F4
    F4 --> F5
    F5 --> F6

    F3 --> G1
    F3 --> G2
    F5 --> G3
    G3 --> G4

    G1 --> H1
    G2 --> H2
    G3 --> H3
    G4 --> H2
    E3 --> H4

    H1 --> I1
    H2 --> I2
    H3 --> I1
    H4 --> I1
    G1 --> I1
    G2 --> I1
    G3 --> I1
    G4 --> I1
    I1 --> I3
```

## Layer Summary

1. External sources provide operational data, policy material, evidence, and human review input.
2. Operational ingestion normalizes hospital-system inputs into canonical event forms.
3. The canonical core stores the platform's stable internal contracts.
4. The state and facts layer reconstructs hospital state and exposes rule-ready facts.
5. The knowledge layer includes source ingestion, curation, and portable runtime knowledge objects.
6. The reasoning layer evaluates rules, applies pathogen and policy logic, and orchestrates execution.
7. The output layer surfaces structured risks, alerts, and reviewable actions.
8. The audit and persistence layer records versions, decisions, and traceability artifacts.
9. The delivery layer exposes the system through API and future UI surfaces.
