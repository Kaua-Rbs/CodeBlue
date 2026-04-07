# Layer Contracts

Status: current
Scope: current architectural layers, module ownership, interface boundaries, and forbidden dependencies
Last meaningful change: 2026-04-05

Purpose: make the current layer ownership, inputs, outputs, and dependency direction explicit before feature growth blurs the boundaries.

This note defines the current layer contracts for CodeBlue. It is meant to stabilize the architectural seams before the implementation grows wider. The goal is not to freeze every internal detail, but to make ownership and interface direction explicit.

## How To Read This Note

Each layer section answers:

- what the layer is for;
- what it owns;
- what it accepts and returns;
- what it may depend on; and
- what it must not absorb from neighboring layers.

The current contracts are intentionally stricter than the current implementation in a few places. When there is a mismatch, the contract should guide future cleanup.

## Architectural Order

The current top-level flow is:

`external data and source knowledge -> adapters and knowledge ingestion -> canonical core -> state and facts -> knowledge runtime -> reasoning and orchestration -> governed outputs and review -> persistence and audit -> API and future UI`

## 1. External Data And Source Knowledge

Purpose:
Provide the raw operational data and source knowledge from which CodeBlue builds its internal representation.

Owns:

- hospital operational events before translation;
- evidence tables and helper tabs;
- local guidelines and flowcharts;
- source metadata that has not yet been normalized.

Inputs:

- hospital system exports;
- spreadsheets;
- documents;
- future external APIs or files.

Outputs:

- raw records for adapters;
- source assets for knowledge ingestion and curation.

Depends on:

- nothing inside the CodeBlue runtime.

Must not depend on:

- internal domain contracts;
- runtime rule objects;
- application services.

Current module anchors:

- source spreadsheets under `seed/knowledge/`;
- future external source connectors outside the current scaffold.

Invariants:

- raw source data is not treated as execution-ready runtime knowledge;
- source format quirks should not leak past ingestion boundaries.

Extension points:

- new hospital sources;
- new source-document formats;
- new evidence-table families.

## 2. Adapters

Purpose:
Translate external operational records into canonical internal events.

Owns:

- source-to-canonical mapping logic for hospital event feeds.

Inputs:

- raw operational records.

Outputs:

- `list[EventEnvelope]`

Depends on:

- canonical event models.

Must not depend on:

- API route code;
- SQLAlchemy ORM models;
- policy logic;
- review logic.

Current module anchors:

- [base.py](/home/kauar/CodeBlue/src/codeblue/adapters/base.py)
- [mock_emr.py](/home/kauar/CodeBlue/src/codeblue/adapters/mock_emr.py)

Primary interface:

- `DataAdapter.map_events(raw_records) -> list[EventEnvelope]`

Invariants:

- adapters emit canonical events, not partially translated custom objects;
- adapter logic is source-specific, not pathogen-specific.

Extension points:

- EMR-specific adapters;
- lab-system adapters;
- bed-management adapters.

## 3. Canonical Core

Purpose:
Define the stable typed internal contracts that the rest of the system uses.

Owns:

- canonical events;
- state models;
- risk models;
- governance models;
- audit models;
- curated knowledge models;
- knowledge-ingestion models.

Inputs:

- validated Python data structures from adapters, services, or persistence.

Outputs:

- typed domain objects used by every higher layer.

Depends on:

- Pydantic and standard-library types only.

Must not depend on:

- FastAPI;
- SQLAlchemy sessions or ORM models;
- route handlers;
- source-file parsing details.

Current module anchors:

- [canonical_events.py](/home/kauar/CodeBlue/src/codeblue/domain/canonical_events.py)
- [state_models.py](/home/kauar/CodeBlue/src/codeblue/domain/state_models.py)
- [risk_models.py](/home/kauar/CodeBlue/src/codeblue/domain/risk_models.py)
- [governance_models.py](/home/kauar/CodeBlue/src/codeblue/domain/governance_models.py)
- [audit_models.py](/home/kauar/CodeBlue/src/codeblue/domain/audit_models.py)
- [knowledge_models.py](/home/kauar/CodeBlue/src/codeblue/domain/knowledge_models.py)
- [knowledge_ingestion_models.py](/home/kauar/CodeBlue/src/codeblue/domain/knowledge_ingestion_models.py)

Invariants:

- domain models remain framework-light;
- the same contracts are used across API, application, packs, and persistence boundaries;
- canonical contracts are not specialized to one pathogen or one hospital.

Extension points:

- new event types;
- richer state/fact models;
- richer knowledge and audit contracts.

## 4. Knowledge Ingestion And Curation

Purpose:
Turn source knowledge into normalized, curated internal knowledge artifacts.

Owns:

- source-sheet classification;
- schema-family detection;
- header normalization;
- helper-sheet parsing;
- source-row normalization;
- the translation boundary between raw knowledge sources and curated runtime knowledge.

Inputs:

- spreadsheets;
- evidence tables;
- local guidelines;
- flowcharts;
- trigger sheets;
- normalization libraries.

Outputs:

- typed ingestion models;
- normalized source rows;
- curated drafts ready to become runtime knowledge bundles.

Depends on:

- knowledge-ingestion domain models;
- file parsing and validation helpers.

Must not depend on:

- API route handlers;
- review decisions;
- persistence internals beyond dedicated repository calls;
- downstream policy execution details.

Current module anchors:

- [knowledge_ingestion.py](/home/kauar/CodeBlue/src/codeblue/services/knowledge_ingestion.py)
- [knowledge_ingestion_models.py](/home/kauar/CodeBlue/src/codeblue/domain/knowledge_ingestion_models.py)
- [knowledge_source_compiler.py](/home/kauar/CodeBlue/src/codeblue/services/knowledge_source_compiler.py)

Invariants:

- raw source tables do not bypass curation into execution-ready bundles;
- source quirks stay upstream;
- helper sheets and synthesis tabs remain distinguishable from execution-ready evidence.

Extension points:

- guideline and flowchart importers;
- row-level validation families;
- curator approval workflows.

Open questions:

- when to persist normalized source rows;
- how much of rule drafting should be automated versus curated manually.

## 5. State And Facts

Purpose:
Rebuild the hospital state over time and expose derived facts for reasoning.

Owns:

- temporal replay;
- patient and staff history reconstruction;
- occupancy snapshots;
- overlap windows;
- fact derivation for the rule and reasoning layers.

Inputs:

- `list[EventEnvelope]`
- `datetime` or time window references

Outputs:

- `StateSnapshotRef`
- fact dictionaries keyed by canonical fact names

Depends on:

- canonical events and state models;
- pure reasoning helpers.

Must not depend on:

- API route logic;
- hospital-specific policy logic;
- source-table parsing.

Current module anchors:

- [state_rebuilder.py](/home/kauar/CodeBlue/src/codeblue/application/state_rebuilder.py)
- [facts_bridge.py](/home/kauar/CodeBlue/src/codeblue/services/facts_bridge.py)

Primary interfaces:

- `TemporalStateRebuilder.rebuild_snapshot(events, as_of) -> StateSnapshotRef`
- `KnowledgeFactsBridge.*_facts(...) -> dict[str, Any]`

Invariants:

- facts refer back to canonical event/state semantics;
- fact derivation uses only information available up to the relevant point in time;
- temporal logic is not embedded inside API routes or persistence models.

Extension points:

- richer exposure models;
- ward-level aggregation;
- resource-state facts for later allocation logic.

## 6. Knowledge Runtime

Purpose:
Represent, load, validate, and execute curated knowledge bundles.

Owns:

- `KnowledgeBundle` loading;
- `RuleArtifact` validation;
- rule DSL evaluation;
- action definitions;
- knowledge test-case execution;
- source-document and evidence linkage inside runtime knowledge.

Inputs:

- curated knowledge bundles;
- fact dictionaries.

Outputs:

- matched rule outputs;
- triggering rule identifiers;
- test results over curated bundles.

Depends on:

- curated knowledge domain models;
- fact dictionaries from the state/facts layer.

Must not depend on:

- HTTP concerns;
- route handlers;
- ORM entities inside evaluator logic.

Current module anchors:

- [knowledge_models.py](/home/kauar/CodeBlue/src/codeblue/domain/knowledge_models.py)
- [knowledge_runtime_models.py](/home/kauar/CodeBlue/src/codeblue/domain/knowledge_runtime_models.py)
- [knowledge_loader.py](/home/kauar/CodeBlue/src/codeblue/services/knowledge_loader.py)
- [rule_evaluator.py](/home/kauar/CodeBlue/src/codeblue/services/rule_evaluator.py)

Primary interfaces:

- `load_knowledge_bundle(path) -> KnowledgeBundle`
- `RuleEvaluator.evaluate_rules(rules, facts) -> RuleEvaluationResult`
- `RuleEvaluator.run_test_case(rules, test_case) -> KnowledgeTestResult`

Invariants:

- rules are stored and evaluated as structured data, not ad hoc code paths;
- evaluator inputs are fact maps plus curated rule objects;
- runtime knowledge remains portable across pathogens and hospitals.

Extension points:

- richer DSL operators;
- per-site bundle selection;
- later integration with model-driven risk features.

## 7. Reasoning And Orchestration

Purpose:
Combine state, facts, pathogen interpretation, scoring, and policy routing into governed outputs.

Owns:

- orchestration flow;
- pathogen-pack execution;
- risk generation;
- policy-pack action proposal;
- end-to-end run coordination.

Inputs:

- canonical events;
- state snapshots;
- pathogen packs;
- policy packs;
- curated knowledge-backed facts and outputs where applicable.

Outputs:

- `RiskAssessment`
- `PriorityAlert`
- `ProposedAction`
- orchestration result objects

Depends on:

- canonical domain models;
- state/facts layer;
- pack interfaces;
- knowledge runtime where pack implementations use it.

Must not depend on:

- direct HTTP request handling;
- raw source-table parsing;
- UI concerns.

Current module anchors:

- [orchestrator.py](/home/kauar/CodeBlue/src/codeblue/application/orchestrator.py)
- [risk_engine.py](/home/kauar/CodeBlue/src/codeblue/application/risk_engine.py)
- [policy_engine.py](/home/kauar/CodeBlue/src/codeblue/application/policy_engine.py)
- [packs/pathogen/base.py](/home/kauar/CodeBlue/src/codeblue/packs/pathogen/base.py)
- [packs/policy/base.py](/home/kauar/CodeBlue/src/codeblue/packs/policy/base.py)
- [packs/pathogen/demo_influenza.py](/home/kauar/CodeBlue/src/codeblue/packs/pathogen/demo_influenza.py)
- [packs/policy/demo_hospital_policy.py](/home/kauar/CodeBlue/src/codeblue/packs/policy/demo_hospital_policy.py)

Primary interfaces:

- `PathogenPack.assess(events, snapshot, time_window, policy_pack_version, scoring_version)`
- `PolicyPack.propose_actions(assessments) -> list[ProposedAction]`
- `OutbreakOrchestrator.run(events) -> OrchestrationResult`

Invariants:

- pathogen packs interpret risk;
- policy packs constrain or surface actions;
- orchestration remains the application boundary that coordinates these steps.

Open questions:

- where the future trained AI risk model should sit relative to pathogen packs and the risk engine;
- how resource-allocation optimization should be introduced without collapsing policy boundaries.

## 8. Review, Governance, And Explainability

Purpose:
Turn proposed actions into human-reviewed outcomes with traceability.

Owns:

- action review decisions;
- action-status transitions;
- explanation generation;
- audit emission for runtime review actions.

Inputs:

- `ProposedAction`
- `ReviewDecision`
- risk and provenance context

Outputs:

- updated action statuses;
- persisted review decisions;
- audit records;
- operator-facing explanations.

Depends on:

- governance and audit domain models;
- repositories dedicated to governance and audit.

Must not depend on:

- raw source ingestion logic;
- adapter-specific mapping logic.

Current module anchors:

- [review_service.py](/home/kauar/CodeBlue/src/codeblue/application/review_service.py)
- [audit.py](/home/kauar/CodeBlue/src/codeblue/services/audit.py)
- [explanation.py](/home/kauar/CodeBlue/src/codeblue/services/explanation.py)

Invariants:

- surfaced actions are reviewable, not autonomous commands;
- every meaningful review transition is auditable;
- explanations should refer to structured provenance rather than ad hoc prose only.

Extension points:

- richer override policy;
- review routing teams;
- later operator UI integration.

## 9. Persistence And Audit Storage

Purpose:
Store append-only operational history and curated runtime artifacts without leaking storage concerns upward.

Owns:

- database sessions and ORM models;
- repository access for events, risks, governance, audit, and knowledge bundles.

Inputs:

- domain/application objects passed through repository interfaces.

Outputs:

- persisted records;
- reconstructed domain/application objects;
- database-backed lookup and replacement operations.

Depends on:

- SQLAlchemy and migration infrastructure;
- domain models for translation.

Must not depend on:

- route-handler logic;
- direct UI concerns;
- source parsing logic.

Current module anchors:

- [db.py](/home/kauar/CodeBlue/src/codeblue/persistence/db.py)
- [orm_models.py](/home/kauar/CodeBlue/src/codeblue/persistence/orm_models.py)
- repositories under [repositories/](/home/kauar/CodeBlue/src/codeblue/persistence/repositories)

Invariants:

- repositories should shield the rest of the system from ORM details;
- persistence is not the place to define policy or outbreak reasoning;
- append-only history and auditability remain first-class.

Extension points:

- richer knowledge persistence;
- site-specific bundle activation;
- more explicit read-model projections later if needed.

## 10. Delivery Layer

Purpose:
Expose the system through HTTP now and UI or integration surfaces later.

Owns:

- FastAPI app setup;
- request and response schemas;
- route wiring;
- dependency injection for application services.

Inputs:

- HTTP requests;
- serialized API payloads.

Outputs:

- HTTP responses;
- operator-facing API contracts.

Depends on:

- application services;
- API schemas;
- settings and dependency wiring.

Must not depend on:

- embedded business logic that bypasses application services;
- direct reasoning or policy logic inside route handlers.

Current module anchors:

- [main.py](/home/kauar/CodeBlue/src/codeblue/api/main.py)
- routes under [routes/](/home/kauar/CodeBlue/src/codeblue/api/routes)
- schemas under [schemas/](/home/kauar/CodeBlue/src/codeblue/api/schemas)

Invariants:

- routes coordinate requests and responses, not business decisions;
- API contracts may evolve, but should remain translations over stable domain/application contracts where possible.

Extension points:

- operator UI;
- external integration API;
- explainability and simulation surfaces.

## What Should Be Treated As Frozen Now

These seams are mature enough to document as current contracts:

- adapter output as canonical events;
- canonical domain models as framework-light shared contracts;
- state snapshot and fact-map boundaries;
- curated knowledge bundle and rule-evaluator boundaries;
- pathogen-pack and policy-pack base interfaces;
- reviewable action and audit boundaries;
- route handlers delegating to application services.

## What Should Not Be Frozen Yet

These parts should stay flexible while the system is still proving itself:

- exact knowledge-source import schema for every future table family;
- final trained-AI interface;
- exact resource-allocation optimizer design;
- internal service/module layout inside the reasoning layer;
- final deployment model for site-specific bundle activation.
