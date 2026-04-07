# Knowledge Source Compiler Plan

Status: in_progress
Scope: immediate implementation plan for compiling the new structured influenza source tables into a hackathon-grade demo bundle and runtime flow
Last meaningful change: 2026-04-07

Purpose: define the minimum knowledge-source compiler and demo path that should be built next from the new architecture-shaped source tables.

This note turns the new table package and its guide into an implementation plan for the current repository. It is intentionally scoped for the hackathon: the goal is not full automation of every source table, but a credible and demonstrable path from structured knowledge sources to reviewable operational recommendations.

## Why This Plan Exists

The new source package in [workbook/](/home/kauar/CodeBlue/workbook) is materially better than the earlier evidence tables for the current stage of CodeBlue.

It already reflects the intended architecture:

- evidence separated by causal stage;
- a compact influenza pathogen pack;
- editable local deployment context;
- policy sources, triggers, actions, and trigger-action mapping.

That means the next useful build step is no longer "parse source tables generically." It is "compile the right subset of these source tables into a coherent demo runtime package."

## Current Fit With The Codebase

The current scaffold already has:

- typed runtime knowledge models in [knowledge_models.py](/home/kauar/CodeBlue/src/codeblue/domain/knowledge_models.py);
- a rule evaluator in [rule_evaluator.py](/home/kauar/CodeBlue/src/codeblue/services/rule_evaluator.py);
- a fact bridge in [facts_bridge.py](/home/kauar/CodeBlue/src/codeblue/services/facts_bridge.py);
- orchestration and pack interfaces in [orchestrator.py](/home/kauar/CodeBlue/src/codeblue/application/orchestrator.py), [base.py](/home/kauar/CodeBlue/src/codeblue/packs/pathogen/base.py), and [base.py](/home/kauar/CodeBlue/src/codeblue/packs/policy/base.py);
- a knowledge-ingestion scaffold in [knowledge_ingestion.py](/home/kauar/CodeBlue/src/codeblue/services/knowledge_ingestion.py);
- typed source-row models for the architecture-shaped CSV package in [knowledge_ingestion_models.py](/home/kauar/CodeBlue/src/codeblue/domain/knowledge_ingestion_models.py); and
- a folder-based CSV package loader for [workbook/](/home/kauar/CodeBlue/workbook);
- a source compiler in [knowledge_source_compiler.py](/home/kauar/CodeBlue/src/codeblue/services/knowledge_source_compiler.py); and
- typed runtime models for compiled deployment profiles, policy triggers, policy actions, and trigger-action mappings in [knowledge_runtime_models.py](/home/kauar/CodeBlue/src/codeblue/domain/knowledge_runtime_models.py).

The main current gap is now after the first runtime execution slice:

- only the first three demo scenarios are executable by the compiled runtime;
- unsupported triggers remain compiled but intentionally skipped at runtime; and
- the pathogen/risk side is still intentionally lightweight compared with the new policy/action path.

## Hackathon Objective

For the hackathon, the system should be able to show this path:

1. load a local influenza deployment profile;
2. ingest a small set of operational events;
3. evaluate influenza-relevant triggers;
4. apply contextual modifiers such as seasonality, vulnerability, spread state, and capacity pressure;
5. surface ranked reviewable actions; and
6. show the source-to-trigger-to-action trace.

This is the shortest path to a strong demo because it proves:

- the system is modular rather than monolithic;
- influenza logic is separated from local deployment settings;
- actions are reviewable rather than autonomous; and
- policy logic is explicit and auditable.

## What Should Be Treated As Executable In V1

The following source tables should be treated as the first executable source set:

- [HSIL - influenza_pack_timing.csv](/home/kauar/CodeBlue/workbook/HSIL%20-%20influenza_pack_timing.csv)
- [HSIL - influenza_pack_risk_features.csv](/home/kauar/CodeBlue/workbook/HSIL%20-%20influenza_pack_risk_features.csv)
- [HSIL - influenza_pack_interventions.csv](/home/kauar/CodeBlue/workbook/HSIL%20-%20influenza_pack_interventions.csv)
- [HSIL - deployment_seasonality_profile.csv](/home/kauar/CodeBlue/workbook/HSIL%20-%20deployment_seasonality_profile.csv)
- [HSIL - policy_source_library.csv](/home/kauar/CodeBlue/workbook/HSIL%20-%20policy_source_library.csv)
- [HSIL - policy_trigger_library.csv](/home/kauar/CodeBlue/workbook/HSIL%20-%20policy_trigger_library.csv)
- [HSIL - action_library.csv](/home/kauar/CodeBlue/workbook/HSIL%20-%20action_library.csv)
- [HSIL - trigger_action_map.csv](/home/kauar/CodeBlue/workbook/HSIL%20-%20trigger_action_map.csv)

These are enough to build a demo compiler and a reviewed decision path.

## What Should Remain Support Material In V1

The following tables should support provenance, feature design, and explainability, but not be fully compiled into the first executable loop:

- [HSIL - ha_influenza_risk_factors.csv](/home/kauar/CodeBlue/workbook/HSIL%20-%20ha_influenza_risk_factors.csv)
- [HSIL - transmission_context_support.csv](/home/kauar/CodeBlue/workbook/HSIL%20-%20transmission_context_support.csv)
- [HSIL - staff_vector_transmission.csv](/home/kauar/CodeBlue/workbook/HSIL%20-%20staff_vector_transmission.csv)

These are valuable immediately for:

- selecting the first fact set;
- grounding explanations; and
- supporting the weighting and prioritization choices in the influenza pack.

## What Should Stay Out Of The First Executable Loop

These tables are useful, but they should not be on the critical path for the first hackathon-grade demo:

- [HSIL - hospitalized_influenza_severity_factors.csv](/home/kauar/CodeBlue/workbook/HSIL%20-%20hospitalized_influenza_severity_factors.csv)
- [HSIL - secondary_infections_in_influenza.csv](/home/kauar/CodeBlue/workbook/HSIL%20-%20secondary_infections_in_influenza.csv)
- [HSIL - pathogen_interactions.csv](/home/kauar/CodeBlue/workbook/HSIL%20-%20pathogen_interactions.csv)
- [HSIL - advanced_outbreak_monitoring_tools - FUTURO.csv](/home/kauar/CodeBlue/workbook/HSIL%20-%20advanced_outbreak_monitoring_tools%20-%20FUTURO.csv)

They mostly deepen later stages:

- established influenza severity;
- secondary infection;
- superinfection microbiology;
- molecular outbreak confirmation.

Those are important, but they complicate the first reviewed operational workflow.

## Compiler Output For V1

The first compiler should produce three kinds of runtime artifacts:

### 1. Curated runtime knowledge

Compile source rows into:

- `SourceDocument`
- `ActionDefinition`
- `RuleArtifact`
- `EvidenceStatement`
- a first influenza `KnowledgeBundle`

### 2. Deployment configuration

Compile deployment profile rows into a dedicated runtime configuration object:

- active seasonality profile;
- local alert window dates or months;
- campaign window;
- manual override settings.

This should remain separate from universal influenza timing rules.

### 3. Demo policy/action graph

Compile:

- trigger definitions;
- stable action definitions; and
- trigger-to-action mappings

into a deterministic decision path that the current orchestrator can use.

## Source Models Already Implemented

The first typed source models for the architecture-shaped source tables now exist instead of forcing those tables through the older generic evidence-row model.

Implemented source models:

- `InfluenzaPackTimingRow`
- `InfluenzaPackRiskFeatureRow`
- `InfluenzaPackInterventionRow`
- `DeploymentSeasonalityProfileRow`
- `PolicySourceRow`
- `PolicyTriggerRow`
- `ActionLibraryRow`
- `TriggerActionMapRow`

These live in the knowledge-ingestion and curation part of the domain layer, not in the runtime bundle models.

## Compiler Status

Already implemented:

- typed source-row models for the new CSV package;
- a folder-based CSV package loader;
- a source compiler that emits:
  - a compiled `KnowledgeBundle`,
  - deployment profiles,
  - policy triggers,
  - policy action catalog entries, and
  - trigger-action mappings.

Now implemented:

- direct execution of compiled trigger-action mappings inside the runtime policy path;
- dynamic fact derivation for the first supported trigger fact set; and
- end-to-end demo wiring that uses the compiled package as the default runtime path in `/runs`.

Still missing:

- broader trigger coverage beyond the first hackathon scenarios;
- richer contextual modifiers beyond deterministic V1 ranking; and
- deeper risk/alert generation to match the stronger compiled action path.

## Minimum Compiler Services Still Missing

Services now added for the first execution slice:

- `deployment_profile_service`
- `policy_trigger_engine`
- `trigger_action_mapper`
- `policy_execution_context_builder`
- compiled runtime cache/loading

Recommended next services:

- `knowledge_source_csv_loader`
  Load the new CSV package from the `workbook/` directory and validate headers.

- richer compiled explainability and trace summarization helpers
  Turn the existing trace payloads into stronger operator-facing narratives.

- optional compiled-risk generator
  Add lightweight risk and alert objects for the same compiled scenarios where they improve the demo.

The key principle is that the compiler and the runtime policy mapping should remain separate:

- the compiler turns source knowledge into structured runtime artifacts;
- the runtime services execute those artifacts against current context.

## Runtime Models Added

The first runtime models needed for the compiled source package now exist:

- `DeploymentProfile`
- `PolicyTriggerDefinition`
- `PolicyActionDefinition`
- `TriggerActionMapping`
- `ContextModifierSet`

These remain compact and demo-focused and preserve the policy/deployment structure of the source package without forcing every field into the older generic bundle models.

## Minimum Fact Set For The Demo

The demo should support only the facts needed by the first trigger/action path.

Recommended initial fact set:

- `seasonality.prealert_active`
- `seasonality.high_alert_active`
- `symptoms.present_at_arrival`
- `case.suspected_or_confirmed_influenza`
- `ward.vulnerability_score`
- `ward.waiting_area_density`
- `capacity.mask_supply_available`
- `capacity.isolation_capacity_pressure`
- `coverage.hcw_vaccination_gap`
- `burden.hospital_respiratory_burden`
- `burden.influenza_specific_hospital_burden`

These can come from:

- direct events;
- deployment profile;
- mock operational context; and
- derived context from the fact bridge.

Do not try to expose the entire workbook feature universe in the first pass.

## Minimum Demo Flow

The first demo flow should be deliberately narrow.

### Scenario A: Front-End Seasonal Activation

Inputs:

- local deployment profile enters pre-alert or high-alert window;
- community activity or hospital respiratory burden rises.

Outputs:

- screening/triage activation review;
- visual alert activation review;
- vaccination-program review.

### Scenario B: Symptomatic Arrival

Inputs:

- patient arrives with respiratory symptoms;
- vulnerable destination ward;
- moderate waiting-area density.

Outputs:

- screen and mask symptomatic person;
- separate symptomatic waiting-area flow review;
- rapid influenza test review.

### Scenario C: Suspected Or Confirmed Inpatient Influenza

Inputs:

- inpatient suspicion or confirmation of influenza;
- current rooming state;
- ward vulnerability;
- capacity pressure.

Outputs:

- droplet-precautions review;
- private-room or cohort review;
- transport limitation review;
- antiviral pathway review where appropriate.

Each scenario should be auditable back to:

- source policy row;
- trigger row;
- action definition;
- trigger-action mapping row; and
- deployment profile where relevant.

## Recommended Code Sequence

Implement in this order:

1. Add a small trigger evaluator and action-mapping service.
2. Wire the compiled outputs into the current policy/review flow.
3. Add one seeded demo scenario per trigger family.
4. Add explainability output that shows source -> trigger -> action -> rationale.

## Acceptance Signal For The Hackathon Build

This path is successful for the hackathon if all of the following are true:

- the new source tables can be loaded from `workbook/` without manual copy-paste into code;
- the influenza pack and deployment profile stay separate;
- at least one seasonal trigger and one inpatient trigger yield structured reviewable actions;
- the surfaced action is traceable to the relevant source rows; and
- the demo clearly shows why CodeBlue is not a single black-box score.

## What This Plan Deliberately Does Not Require

This plan does not require:

- a trained predictive model;
- full automation of literature-to-rule translation;
- support for all tables in the source package;
- full hospital-specific guideline ingestion;
- production-grade optimization or simulation.

Those can come later. The purpose here is to demonstrate the architecture honestly and effectively.

## Recommended Immediate Repository Changes

The next repository changes should be:

1. add a narrow trigger/action execution path for the first demo scenarios;
2. wire the compiled deployment, trigger, action, and mapping artifacts into the runtime policy path; and
3. add a seeded API walkthrough that uses the new compiled artifacts instead of only the current hard-coded demo pack.
