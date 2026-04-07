# Knowledge Roadmap

Status: current
Scope: implemented knowledge-layer scope versus intentionally deferred work
Last meaningful change: 2026-04-05

Purpose: record what the current knowledge implementation already proves and what has been deferred to later phases on purpose.

This document records what the current knowledge-layer implementation covers and what is intentionally deferred.

## What Is Implemented Now

The current scaffold includes:

- a minimal typed knowledge bundle model;
- a knowledge-ingestion scaffold that can parse multi-sheet source knowledge before bundle translation;
- typed source-row models for the architecture-shaped CSV source package;
- a CSV package loader for the `workbook/` directory;
- a source compiler that emits a compiled `KnowledgeBundle` plus deployment, trigger, action, and mapping runtime objects;
- a generic `RuleArtifact` instead of many specialized rule tables;
- a validated rule DSL with boolean groups and a small operator set;
- typed rule outputs for classifications, constraints, proposed actions, notifications, and exposure flags;
- persistence for bundles, packs, source documents, actions, evidence, terminology bindings, rules, and knowledge test cases;
- a deterministic evaluator that executes rules against flat fact dictionaries; and
- a small fact bridge that derives the first demo facts from the canonical event/state layer.

The current demo path uses the knowledge layer for:

- hospital-onset influenza case classification;
- review-action generation for isolation placement; and
- policy-constraint evaluation for surfaced actions.

The current ingestion-and-curation submodule does not yet auto-generate rules. It is intentionally upstream of the runtime bundle objects while still belonging to the broader knowledge layer.

The newly structured source package in [workbook/](/home/kauar/CodeBlue/workbook) now has both a typed loader path and a compiler path. Source tables for influenza-pack content, deployment profile, triggers, actions, and trigger-action mappings can already be compiled into a hackathon-grade runtime package before the broader evidence tables are fully automated.

## Deferred Phase 1: DSL Expansion

Defer the following until the first evaluator contract is proven:

- time-relative operators such as `within_last_hours` and `within_last_days`;
- explicit overlap-aware operators such as `overlaps_with`;
- richer aggregation and counting semantics;
- more complex value transforms; and
- additional output types beyond the current minimal set.

## Deferred Phase 2: Knowledge Model Expansion

Keep the generic rule model for now. Only split into richer domain-specific artifacts if the current abstraction becomes limiting.

Candidates for later expansion:

- `PathogenParameter`
- `InterventionAssumption`
- `OverridePolicy`
- `RuleAuditRecord`
- `DecisionAuditRecord`
- `ChangeLog`

## Deferred Phase 3: Editing And Ingestion Tooling

The current implementation loads a seed bundle and includes a first knowledge-source parser scaffold. Later work can add:

- YAML and JSON authoring workflows;
- import and export tools;
- a validation CLI;
- source-knowledge persistence and row-level normalization pipelines;
- trigger-sheet translation into structured surveillance logic;
- structured translation workflows from prose source documents; and
- reviewer approval workflows for translated rules.

## Deferred Phase 4: Full Pack Runtime

The current pack wrappers are still Python classes, and the source compiler now produces deployment, trigger, action, and mapping runtime artifacts. Later work should:

- make pathogen, policy, and workflow packs fully data-driven;
- reduce Python pack code to execution infrastructure and fact derivation;
- execute compiled trigger-action mappings directly inside the runtime policy path;
- extend routing and escalation behavior; and
- let knowledge bundles be selected or swapped dynamically at runtime.

## Why Deferred

These items are deferred to avoid overbuilding before the following are proven:

- the rule DSL is expressive enough for the first real use cases;
- the evaluator semantics are stable and testable;
- the derived-fact model is correct;
- the knowledge bundle structure is practical for authors; and
- the current data-driven path produces reliable, auditable actions.
