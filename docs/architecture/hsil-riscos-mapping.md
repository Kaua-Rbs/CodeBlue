# HSIL RISCOS Mapping

Status: current
Scope: mapping of the `HSIL - RISCOS.csv` source table into the current knowledge layer
Last meaningful change: 2026-04-05

Purpose: explain what the first HSIL RISCOS table can support now, what only maps as evidence, and what remains deferred.

This note explains how the table in [HSIL - RISCOS.csv](/home/kauar/Downloads/HSIL%20-%20RISCOS.csv) maps into the current Phase 0 knowledge layer.

## What Was Added

A first draft bundle now exists at [hsil_riscos_bundle_draft.json](/home/kauar/CodeBlue/seed/knowledge/hsil_riscos_bundle_draft.json).

It contains:

- one `SourceDocument` entry per table row;
- one `EvidenceStatement` per study-level finding cluster;
- a small set of `RuleArtifact` candidates that the current DSL can express safely; and
- one draft `ActionDefinition` plus one draft `KnowledgeTestCase`.

## What Maps Cleanly To The Current DSL

These patterns from the table work well with the current DSL:

- hospital-onset thresholds such as `>48h`, `>=72h`, or `>=5 days` after admission
- room-structure signals such as `double-occupancy rooms`
- direct categorical triggers that can become facts
- governance-style constraints such as forcing review-only behavior and logging

Examples now represented in the draft bundle:

- `lab.confirmed_pathogen == influenza`
- `encounter.hours_since_admission > 48`
- `room.type == double_room`
- `classification.case_classification exists`
- `proposed_action.category == medication`

## What Only Maps As Evidence Right Now

A large part of the table is useful, but not yet executable in the current Phase 0 evaluator.

This includes:

- odds ratios, hazard ratios, and multivariable statistical findings
- SHAP feature rankings and model AUCs
- free-text severity summaries
- regional seasonality and bulletin-based adaptation logic
- nuanced diagnostic-lag comparisons
- findings that require facts the current fact bridge does not expose

These were stored as `EvidenceStatement` material, not as executable rules.

## Deferred Candidate Rules

The table suggests several good future rules that the current implementation should not execute yet because the needed facts or operators do not exist:

- pediatric paradoxical breathing escalation
- oncology/SCT ward new-onset alerts
- fresh chemotherapy auto-ICU alerts
- seasonal adaptation rules based on region and bulletin timing
- feature-based deterioration screening from ML studies

Those belong to later phases once the fact bridge and DSL are expanded.

## Practical Recommendation

Treat the HSIL table as:

1. provenance material for knowledge ingestion,
2. evidence support for future pathogen and governance packs,
3. a source of candidate rules to be translated selectively.

Do not treat it as directly executable policy logic without manual structuring.
