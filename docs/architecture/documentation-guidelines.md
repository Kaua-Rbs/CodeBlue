# Documentation Guidelines

Status: current
Scope: repository-wide documentation rules for architecture, interfaces, and decision records
Last meaningful change: 2026-04-05

Purpose: define the default documentation discipline for CodeBlue so architectural reasoning and interface changes stay clear over time.

This note defines the documentation rules that should be followed as CodeBlue evolves. The goal is to keep the thought process, architectural decisions, and interface boundaries clear enough to revisit later without rebuilding the reasoning from scratch.

## Purpose

CodeBlue is already accumulating several kinds of documentation:

- high-level product framing;
- architecture views and diagrams;
- domain-model notes;
- development plans;
- data and knowledge-design notes; and
- implementation-specific backend notes.

Without explicit rules, those documents will drift, repeat each other, and eventually stop being trusted. These guidelines are the default discipline for keeping the documentation useful.

## Core Rules

### 1. One Concept, One Home

Each important concept should have one primary document that owns its explanation.

Examples:

- `KnowledgeBundle` and the broader knowledge model should have one primary architecture note.
- canonical schema rules should have one primary schema note.
- layer responsibilities should have one primary layer-contract note.

Other documents should link to that source instead of redefining the concept with slightly different wording.

### 2. Update Documentation In The Same Change As Interface Changes

If a code change modifies any of the following, the related documentation must be updated in the same change:

- public API routes;
- domain models;
- architectural layer responsibilities;
- pack interfaces;
- bundle, rule, or ingestion schemas;
- persistence contracts; or
- naming of major concepts.

If the contract changed but the documentation did not, the change is incomplete.

### 3. Prefer Why, Invariant, And Interface Over Narrative

Documentation should primarily answer:

- why this exists;
- what it owns;
- what must remain true; and
- what goes in and out.

Long narrative explanation is fine when needed, but the stable value is usually in constraints and interfaces, not storytelling.

### 4. Distinguish Current, Draft, And Superseded Material

Each architecture note should declare:

- `Status`
- `Scope`
- `Last meaningful change`

If a note is no longer current, mark it as superseded and point to the replacement. Do not silently leave obsolete docs in place.

### 5. Diagrams Summarize; Prose Owns The Contract

Diagrams are presentation tools and orientation aids. They should not be the only place where responsibilities or interfaces are defined.

The source of truth should be short prose plus explicit contracts.

### 6. Record Significant Decisions Explicitly

Nontrivial architectural choices should be recorded as short decision notes under `docs/architecture/decisions/`.

Each decision note should state:

- what was chosen;
- why it was chosen;
- which alternatives were rejected; and
- what the decision now constrains or enables.

These notes should stay concise. They are a memory aid, not essays.

### 7. Record Deprecation Instead Of Erasing Context

When a concept or name is replaced, add a short note that says it was superseded and what replaced it.

This is especially important when:

- a layer is renamed;
- an interface is replaced;
- a data model is collapsed or split; or
- a design idea is intentionally abandoned.

### 8. Keep Documentation Close To Stable Boundaries

The best candidates for durable documentation are:

- layer ownership;
- interface contracts;
- invariants;
- extension points;
- deployment units;
- provenance and audit rules; and
- reasoning behind major tradeoffs.

Do not spend the same effort documenting low-value transient details that can be read directly from the code.

## Required Structure For Architecture Notes

Every new architecture note should, at minimum, include:

- `Status`
- `Scope`
- `Last meaningful change`
- a short statement of purpose

When the note describes a module or architectural slice, it should also include the contract fields below when relevant:

- `Purpose`
- `Owns`
- `Inputs`
- `Outputs`
- `Depends on`
- `Must not depend on`
- `Invariants`
- `Extension points`
- `Open questions`

Not every note needs every field, but module and layer notes usually should.

## Recommended Document Split

Use the following split by default:

- `README.md`
  Product framing, repository entrypoint, current status, and links outward.

- `docs/architecture/*.md`
  Layer boundaries, decision rationale, system diagrams, module contracts, and knowledge architecture.

- `docs/schema/*.md`
  Canonical data-shape explanations and schema invariants.

- `docs/development-plan.md`
  Active implementation plan and sequencing, not final architecture truth.

- `docs/architecture/decisions/*.md`
  Short architectural decision records for important choices.

## When To Create A New Document

Create a new note when:

- a concept would otherwise be explained in more than one place;
- a boundary deserves its own contract;
- a design decision needs to be discoverable later; or
- a document is starting to mix unrelated concerns.

Do not create a new note just to restate an existing one with different wording.

## Minimal Maintenance Checklist

When making a meaningful change, check:

1. Did any interface, schema, or route change?
2. Does an existing architecture note own that concept?
3. If yes, was it updated in the same change?
4. If no, does a new note need to be created?
5. If an older note is no longer correct, was it marked or replaced?

## Definition Of Good Documentation In This Repo

Good documentation in CodeBlue should let a future reader answer these questions quickly:

- what is this part of the system for;
- what does it own;
- what does it accept and produce;
- what does it depend on;
- what is still intentionally flexible; and
- why was this design chosen instead of nearby alternatives.

If a note cannot answer those questions, it is probably too vague to be useful.
