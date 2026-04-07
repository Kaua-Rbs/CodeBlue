# Knowledge Ingestion And Curation

Status: current
Scope: upstream knowledge-source handling inside the broader knowledge layer
Last meaningful change: 2026-04-05

Purpose: explain how CodeBlue takes source knowledge, normalizes it, curates it, and prepares it for execution without letting source-format quirks leak into runtime knowledge.

This note describes the upstream part of the knowledge layer: how CodeBlue takes source knowledge, normalizes it, curates it, and prepares it for execution.

In the current repository, the first source format happens to be a live multi-tab spreadsheet. That spreadsheet is only one kind of knowledge source. Conceptually, this part of the system is the ingestion and curation submodule of the broader knowledge layer.

## What This Part Of The Knowledge Layer Does

The knowledge layer now has two broad responsibilities:

1. `Knowledge ingestion and curation`
   Read source knowledge such as evidence tables, helper sheets, local guidelines, trigger notes, and hospital flowcharts, then normalize and validate them.

2. `Knowledge runtime`
   Store curated knowledge as typed internal objects such as bundles, packs, rules, evidence statements, action definitions, and test cases that the system can execute.

This first responsibility is necessary because source knowledge is usually not already in runtime form.

## Why The Source Tables Should Not Bypass Curation

The influenza workbook is valuable source knowledge, but it is still source knowledge.

It contains:

- multiple schema families rather than one universal table shape;
- helper/reference tabs such as `library`, abbreviations, and trigger notes;
- synthesis/staging tabs such as `Riscos.2`;
- title-row and duplicate-header quirks;
- routing and curation metadata such as `factor_role` and `data_status`; and
- normalization work that still has to happen before the data becomes execution-ready.

If the runtime knowledge model had to absorb all of that directly, it would become a mixed ETL-plus-execution layer. That would make the core knowledge objects harder to validate, version, and reason about.

## How This Fits The Broader Knowledge Layer

The cleaner structure is:

### `Knowledge sources`

- influenza evidence tables;
- hospital-specific guideline documents;
- hospital flowcharts;
- normalization libraries;
- trigger sheets; and
- later, pathogen-specific reference material.

### `Knowledge ingestion and curation`

- import source spreadsheets or other artifacts;
- normalize aliases to canonical features;
- validate timing semantics and leakage boundaries;
- classify rows by role and readiness;
- separate synthesis content from execution-ready evidence; and
- translate curated content into structured internal objects.

### `Curated knowledge objects`

- `KnowledgeBundle`
- `SourceDocument`
- `PathogenPack`
- `PolicyPack`
- `ReviewWorkflowPack`
- `RuleArtifact`
- `EvidenceStatement`
- `ActionDefinition`
- `KnowledgeTestCase`

### `Knowledge runtime`

- bundle loading;
- rule evaluation;
- policy and workflow routing;
- versioning and provenance; and
- later dynamic bundle selection per site.

## Current Implementation In The Repo

The repository now includes the first scaffold for the ingestion-and-curation part of the knowledge layer:

- typed ingestion models in [knowledge_ingestion_models.py](/home/kauar/CodeBlue/src/codeblue/domain/knowledge_ingestion_models.py);
- a source-spreadsheet parser in [knowledge_ingestion.py](/home/kauar/CodeBlue/src/codeblue/services/knowledge_ingestion.py);
- typed source-row models for the architecture-shaped CSV package under [workbook/](/home/kauar/CodeBlue/workbook);
- a folder-based CSV package loader in [knowledge_ingestion.py](/home/kauar/CodeBlue/src/codeblue/services/knowledge_ingestion.py);
- a source compiler in [knowledge_source_compiler.py](/home/kauar/CodeBlue/src/codeblue/services/knowledge_source_compiler.py);
- typed runtime models for compiled deployment profiles, policy triggers, policy actions, and trigger-action mappings in [knowledge_runtime_models.py](/home/kauar/CodeBlue/src/codeblue/domain/knowledge_runtime_models.py);
- schema-family and source-sheet detection for the live influenza workbook; and
- unit tests for title-row skipping, duplicate-header skipping, synthesis-sheet separation, helper-sheet parsing, CSV package loading, and source-package compilation in [test_knowledge_ingestion.py](/home/kauar/CodeBlue/tests/unit/test_knowledge_ingestion.py) and [test_knowledge_source_compiler.py](/home/kauar/CodeBlue/tests/unit/test_knowledge_source_compiler.py).

This scaffold is intentionally upstream-facing. It can now parse both the older workbook-style source format and the newer folder-based CSV package, and it can compile the newer source package into runtime artifacts. It still does not execute those compiled artifacts end to end inside the orchestration flow yet.

## How Hospital-Specific Knowledge Should Integrate

For hospital-specific deployment, the clean path is:

1. keep the influenza evidence tables as source material for the first pathogen pack;
2. ingest hospital-specific guidelines and flowcharts as policy/workflow source knowledge;
3. translate that local material into structured policy and workflow objects;
4. package pathogen, policy, workflow, and terminology content into a site-specific `KnowledgeBundle`; and
5. activate the appropriate bundle version for that hospital.

That keeps the workflow simple:

- evidence tables shape the pathogen logic;
- local guidelines shape the hospital policy pack and review workflow pack; and
- the runtime system executes only the curated bundle, not the raw source files.

## What Comes Next

The next development step for this part of the knowledge layer should be:

- persist imported knowledge-source metadata and normalized rows;
- add stronger row-level validation for compact, extended, and legacy-aware evidence schemas;
- execute compiled trigger and trigger-action artifacts against runtime facts;
- drive canonical feature normalization from the `library` tab;
- keep synthesis tabs separate from execution-ready evidence; and
- deepen the translation boundary from curated source rows into executable runtime artifacts.

Short version: the spreadsheet is the first source of knowledge, not the final runtime representation of knowledge. The knowledge layer now includes both source ingestion/curation and executable knowledge runtime, which is the cleaner architecture for CodeBlue.
