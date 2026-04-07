# Project Owner Brief

Status: current
Scope: consolidated owner-level reference for CodeBlue product intent, architecture, major decisions, current implementation state, and immediate direction
Last meaningful change: 2026-04-05

Purpose: give the current owner and sole engineer one document that restores the full working mental model of the project quickly without needing to reread every architecture note.

This is the condensed project memory for CodeBlue. It is the place to reread before making major product, architecture, or implementation decisions.

## Executive Summary

CodeBlue is a modular hospital outbreak decision-support platform.

Its job is to:

- ingest hospital operational events;
- reconstruct a time-aware internal view of what is happening in the hospital;
- interpret that state using pathogen knowledge plus local policy/workflow knowledge;
- prioritize reviewed operational actions that may reduce spread; and
- preserve auditability across the full reasoning path.

The current first-version target is not a production hospital deployment. It is a hackathon-grade, influenza-first backend proof of concept that demonstrates the architecture, the reasoning flow, and the governed action model.

## What The Product Is

CodeBlue is meant to be a:

- stable core platform for outbreak reasoning;
- portable knowledge system across pathogens and hospitals; and
- human-supervised decision-support system rather than an autonomous control system.

The core promise is:

`hospital events + portable knowledge + governed reasoning -> reviewable outbreak actions`

## What The Product Is Not

CodeBlue is not currently intended to be:

- a polished production UI;
- a fully trained hospital-grade predictive ML platform;
- an autonomous order-entry or command system;
- a one-pathogen hard-coded tool; or
- a hospital-specific one-off prototype.

The current build should prove the platform logic, not pretend the final production system already exists.

## The Current High-Level Definition

Yes, the high-level aspects are now solid enough to treat as defined.

The following are already stable enough to guide development:

- the core product goal;
- the layer boundaries;
- the stable-versus-variable split;
- the knowledge-layer design;
- the Phase 0 scope;
- the hackathon-oriented proof path;
- the documentation discipline; and
- the current implementation direction from source knowledge to runtime artifacts.

The following are still intentionally flexible:

- the final AI model design;
- the exact trigger-execution runtime path;
- hospital-specific policy authoring workflows;
- deeper temporal/exposure semantics;
- the final UI; and
- post-hackathon production concerns.

That is a healthy state. The backbone is defined even though several downstream components are still scaffold or planned.

## Core Product Principle

The most important architectural principle is:

**The stable platform must remain separate from the knowledge that changes by pathogen, deployment, and hospital policy.**

That leads to the central split:

- stable platform core;
- portable curated knowledge;
- reviewed actions;
- auditability everywhere.

## Stable Versus Variable Parts

Stable platform parts:

- canonical event and domain contracts;
- temporal state reconstruction;
- fact derivation;
- orchestration flow;
- governed output contracts;
- audit and provenance model;
- API shell;
- knowledge runtime abstractions.

Variable parts:

- external hospital adapters;
- pathogen-specific knowledge packs;
- hospital-specific policy and workflow packs;
- deployment profiles;
- source knowledge assets;
- presentation details.

If a future change threatens this separation, it should be treated as a design smell.

## Current Architecture In One Page

The current architectural flow is:

`external hospital data and source knowledge -> adapters and knowledge ingestion -> canonical core -> state and facts -> knowledge runtime -> reasoning and orchestration -> governed outputs and review -> persistence and audit -> API and future UI`

The presentation-friendly summary is:

`hospital data -> canonical event/state core -> reasoning engine fed by knowledge packs -> governed actions -> human review -> audit -> API/UI`

## Layer Summary

### 1. External Data And Source Knowledge

Owns:

- hospital operational records before translation;
- source knowledge tables;
- guidelines;
- flowcharts;
- evidence documents.

This layer is upstream input only. It is not execution-ready runtime knowledge.

### 2. Adapters

Owns:

- translation from external operational data into canonical events.

Adapters are source-specific, not pathogen-specific.

### 3. Canonical Core

Owns:

- typed internal contracts for events, state, risk, governance, audit, and knowledge.

This is the stable language of the platform.

### 4. Knowledge Ingestion And Curation

Owns:

- source-knowledge loading;
- normalization;
- schema-family handling;
- source-row modeling;
- translation into curated runtime artifacts.

This is part of the broader knowledge layer, not a separate top-level system anymore.

### 5. State And Facts

Owns:

- temporal replay;
- occupancy and overlap reconstruction;
- fact derivation for rules and reasoning.

This is the bridge between raw hospital history and executable logic.

### 6. Knowledge Runtime

Owns:

- bundles;
- packs;
- rules;
- actions;
- evidence;
- terminology bindings;
- deployment profiles;
- policy triggers;
- trigger-action mappings.

This is the execution-ready knowledge surface.

### 7. Reasoning And Orchestration

Owns:

- pathogen interpretation;
- risk generation;
- policy evaluation;
- action generation;
- run orchestration.

This layer should consume facts and curated knowledge, not raw source tables.

### 8. Governed Outputs And Review

Owns:

- proposed actions;
- review routing;
- accept/reject/defer/escalate/override flow.

This exists because CodeBlue should support reviewed decisions, not direct autonomous actions.

### 9. Persistence And Audit

Owns:

- append-only event storage;
- persisted risks, actions, reviews, and audit records;
- version and provenance traceability.

### 10. API And Future UI

Owns:

- the delivery surface.

The API is current. A real operator UI is later.

## Knowledge Architecture You Should Keep In Mind

CodeBlue does not treat knowledge as loose documents. It treats knowledge as typed, versioned, curated objects.

The main knowledge concepts are:

- `KnowledgeBundle`: deployable unit of knowledge;
- `SourceDocument`: provenance;
- `PathogenPack`: disease-specific logic;
- `PolicyPack`: local operational constraints;
- `ReviewWorkflowPack`: routing and review behavior;
- `RuleArtifact`: executable typed rule abstraction;
- `ActionDefinition`: controlled action catalog;
- `EvidenceStatement`: reusable evidence layer;
- `TerminologyBinding`: local-to-canonical mapping;
- `KnowledgeTestCase`: regression tests for knowledge behavior.

The key reason for this design is that CodeBlue must solve two things at once:

- represent outbreak logic in a machine-usable way; and
- keep that logic portable, reviewable, and replaceable across hospitals and pathogens.

## Why Knowledge Ingestion And Curation Exists

Source knowledge is not runtime knowledge.

Even when the source is highly structured, it still contains:

- source-format quirks;
- helper/reference tables;
- synthesis material;
- local wording;
- normalization work;
- incomplete execution semantics.

The ingestion-and-curation submodule exists to prevent those source concerns from leaking into the execution layer.

That is why the current architecture absorbed the earlier "workbook layer" idea into the broader knowledge layer under a better name.

## Current Knowledge Source Strategy

There are two relevant source-knowledge generations in the repo:

- earlier evidence-oriented source tables;
- the newer architecture-shaped CSV package in [workbook/](/home/kauar/CodeBlue/workbook).

The newer package is the current strategic source for the hackathon because it is already closer to the intended runtime model.

The most important tables in that package are:

- influenza pack timing;
- influenza pack risk features;
- influenza pack interventions;
- deployment seasonality profile;
- policy source library;
- policy trigger library;
- action library;
- trigger-action map.

These are now treated as the narrow executable source set for the hackathon path.

## What Has Already Been Implemented

The repository already includes:

- project bootstrap, environment definition, lint/type/test scaffolding, and Docker;
- typed domain contracts for canonical events, state, risk, governance, audit, knowledge, and knowledge ingestion;
- initial persistence models and migrations;
- a temporal state rebuilder;
- pack interfaces for adapters, pathogen packs, and policy packs;
- a deterministic rule evaluator;
- a fact bridge;
- a knowledge-ingestion service;
- typed source-row models for the new CSV package;
- a folder-based CSV package loader for [workbook/](/home/kauar/CodeBlue/workbook);
- a source compiler that produces a compiled bundle plus deployment, trigger, action, and mapping runtime objects;
- a demo pathogen pack and demo policy pack;
- FastAPI routes for health, events, state, runs, risks, actions, review, and explainability;
- seed/demo data and initial tests.

This means the project is no longer just architecture notes. It now has a real scaffold with a clear direction.

## What The Source Compiler Already Proves

The source compiler already proves that CodeBlue can:

- load the structured source package;
- model source rows as typed objects;
- compile them into runtime knowledge artifacts;
- separate deployment context from pathogen content;
- separate triggers from actions;
- preserve provenance links; and
- generate a hackathon-grade compiled bundle rather than relying only on hand-authored demo logic.

This is a meaningful milestone because it is the first concrete bridge from knowledge-source assets to runtime artifacts.

## What Is Still Missing On The Critical Path

The most important gap now is downstream runtime execution.

What is still missing:

- compiled trigger evaluation against live runtime facts;
- execution of compiled trigger-action mappings inside the policy/runtime path;
- richer temporal exposure logic;
- stronger explainability linkage from source row to surfaced action;
- more complete integration tests in a fully provisioned environment.

In short:

- upstream compilation is now real;
- downstream runtime execution is the next major step.

## Hackathon Scope

The hackathon version should demonstrate:

- influenza-first reasoning;
- local deployment profile awareness;
- explicit triggers;
- governed reviewable actions;
- human review;
- provenance and traceability.

It does not need to demonstrate:

- real hospital integration;
- production-grade ML training;
- a fully operational front-end;
- a fully generalized multi-pathogen platform.

The hackathon objective is a convincing proof of architecture and decision logic.

## Current AI Positioning

The cleanest current interpretation is:

- the stable system boundary for action generation is governed and review-based;
- any future AI or model component should support prioritization and reasoning, not bypass governance;
- the first production-grade ML model is not yet defined and should not be faked;
- for the hackathon, the architecture should remain compatible with a future risk model without making current progress depend on it.

This means the platform can already show decision-support logic even while the exact ML path remains open.

## Non-Negotiable Invariants

These are the architectural rules worth keeping at the front of your mind:

- canonical internal contracts stay framework-light and pathogen-agnostic;
- source knowledge never bypasses curation into runtime artifacts;
- pathogen logic does not leak into the stable platform core;
- policy/governance stays separate from pathogen truth;
- reviewable actions are the boundary, not autonomous commands;
- audit and provenance are not optional extras;
- packs and bundles must remain swappable without rewriting the core;
- documentation must be updated when interfaces or ownership boundaries change.

If a change weakens these, it should be challenged.

## Decisions That Are Already Made

The following decisions should be treated as current unless there is a strong reason to revisit them:

- Python 3.12 backend-first architecture;
- FastAPI + Pydantic + SQLAlchemy + Alembic + PostgreSQL;
- Conda as the current local environment path in this repo;
- a typed canonical schema as the stable platform language;
- a knowledge bundle as the deployable unit of logic;
- generic `RuleArtifact` first, not many specialized rule tables;
- JSON-like typed DSL for executable conditions and outputs;
- reviewed operational actions instead of direct execution;
- knowledge ingestion and curation as a submodule inside the broader knowledge layer;
- the new `workbook/` CSV package as the current primary hackathon source package;
- narrow hackathon scope rather than broad over-implementation.

## Things That Are Intentionally Not Decided Yet

These should remain open for now:

- whether the eventual risk engine is heuristic, statistical, or ML-backed;
- the exact final fact vocabulary;
- the final hospital guideline authoring workflow;
- the final operator UI;
- post-hackathon deployment topology;
- whether the generic rule model later needs richer specialization.

Keeping these open is deliberate, not a sign that the architecture is weak.

## Main Risks To Avoid

The main project risks at this stage are:

- overbuilding before the runtime path is proven;
- mixing source-ingestion concerns into runtime logic;
- hard-coding influenza assumptions into the stable platform;
- building presentation surface faster than reasoning quality;
- promising AI behavior that the current data does not justify;
- letting documentation drift from actual interfaces;
- adding more source coverage before the current source package is executed end to end.

## What You Should Say If You Need To Explain The Project Quickly

Use this framing:

CodeBlue is a hospital outbreak decision-support platform. It reconstructs hospital state from operational events, combines that with curated pathogen and policy knowledge, and produces reviewable actions with full traceability instead of autonomous commands. The current proof of concept is influenza-first, but the architecture is designed so pathogens, policies, and deployment context can be swapped without rewriting the core system.

## Current Recommended Next Step

The current best next step is:

**wire the compiled source package into a narrow runtime trigger-and-action execution path.**

That means:

- evaluate compiled triggers against facts;
- apply trigger-action mappings plus contextual modifiers;
- surface ranked reviewable actions;
- expose traceability from source knowledge to action.

That is the shortest path from the current scaffold to a compelling demo.

## Where To Look First In The Repo

If you need to reorient quickly, start here:

- [README.md](/home/kauar/CodeBlue/README.md)
- [layer-contracts.md](/home/kauar/CodeBlue/docs/architecture/layer-contracts.md)
- [backend-slice.md](/home/kauar/CodeBlue/docs/architecture/backend-slice.md)
- [knowledge-ingestion-and-curation.md](/home/kauar/CodeBlue/docs/architecture/knowledge-ingestion-and-curation.md)
- [knowledge-source-compiler-plan.md](/home/kauar/CodeBlue/docs/architecture/knowledge-source-compiler-plan.md)
- [development-plan.md](/home/kauar/CodeBlue/docs/development-plan.md)

For code:

- [orchestrator.py](/home/kauar/CodeBlue/src/codeblue/application/orchestrator.py)
- [knowledge_ingestion.py](/home/kauar/CodeBlue/src/codeblue/services/knowledge_ingestion.py)
- [knowledge_source_compiler.py](/home/kauar/CodeBlue/src/codeblue/services/knowledge_source_compiler.py)
- [rule_evaluator.py](/home/kauar/CodeBlue/src/codeblue/services/rule_evaluator.py)
- [facts_bridge.py](/home/kauar/CodeBlue/src/codeblue/services/facts_bridge.py)
- [knowledge_models.py](/home/kauar/CodeBlue/src/codeblue/domain/knowledge_models.py)
- [knowledge_ingestion_models.py](/home/kauar/CodeBlue/src/codeblue/domain/knowledge_ingestion_models.py)
- [knowledge_runtime_models.py](/home/kauar/CodeBlue/src/codeblue/domain/knowledge_runtime_models.py)

## The One-Sentence Mental Model

If you forget everything else, remember this:

**CodeBlue is a time-aware, knowledge-driven, governed outbreak reasoning platform whose job is to turn hospital events into reviewable, auditable actions without hard-coding one pathogen or one hospital into the core.**
