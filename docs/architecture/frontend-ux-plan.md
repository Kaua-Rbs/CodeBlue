# Frontend UX Plan

Status: draft
Scope: recommended hackathon and Phase 0 frontend structure, information architecture, screens, and interaction model
Last meaningful change: 2026-04-05

Purpose: define the first frontend shape for CodeBlue so the product can be presented clearly and the backend can evolve toward a coherent operator experience.

This note describes what the frontend should be for the hackathon and early product slice. It is intentionally product-focused rather than implementation-focused.

The concrete screen-level follow-up lives in [frontend-screen-spec.md](/home/kauar/CodeBlue/docs/architecture/frontend-screen-spec.md).

## Product Goal For The Frontend

The frontend should help an operator answer four questions quickly:

- what is happening right now;
- where the highest operational risk is;
- what should be reviewed first; and
- why the system is recommending that action.

The frontend is not just a technical wrapper around API routes. It is the operational face of the product.

## Primary User For V1

The primary user should be treated as:

- an infection prevention or hospital operations lead;
- someone triaging multiple signals under time pressure; and
- someone who needs trust, traceability, and prioritization more than raw detail.

Secondary users later can include:

- bedside clinicians;
- stewardship teams;
- unit managers;
- hospital epidemiology staff; and
- policy or quality reviewers.

For the hackathon, optimize for the primary user only.

## Core UX Principles

### 1. Operations First

The UI should prioritize decisions and priorities, not raw data browsing.

### 2. Overview Before Detail

The first screen should answer:

- what changed;
- what is urgent; and
- where attention should go.

Then let the user drill down.

### 3. Trust Before Automation

Every important recommendation should show:

- target;
- urgency;
- reason;
- source logic; and
- review options.

### 4. Dense But Legible

This is an operations tool, not a marketing site. It should feel deliberate, calm, and information-rich without becoming cluttered.

### 5. Human Review Is Central

The UI should present actions as:

- proposed;
- governed;
- reviewable.

It should never feel like the system is silently issuing orders.

## Recommended Information Architecture

For the hackathon and Phase 0, keep the product to four main surfaces:

1. Command Center
2. Action Review Workspace
3. Ward Detail View
4. System Context And Trace View

That is enough to show the product clearly without overbuilding.

## 1. Command Center

This should be the default landing screen and the anchor of the demo.

Its job is to give immediate situational awareness.

### What The User Should See

- current alert state;
- current deployment profile or influenza seasonality state;
- last run time;
- high-priority pending actions;
- highest-risk wards or units;
- capacity pressure indicators;
- current hospital respiratory burden;
- recent trigger activity.

### Recommended Layout

Top bar:

- hospital/site name;
- current seasonality state;
- last orchestration run;
- prominent `Run Assessment` control.

Top summary band:

- pending high-priority actions;
- high-risk wards count;
- isolation capacity pressure;
- vaccination or preparedness gap;
- active review queue size.

Main content:

- left: prioritized action queue;
- center: ward risk board;
- right: trigger and system-status panel.

### Most Important Interactions

- run a fresh assessment;
- open the highest-priority action;
- open a ward detail view;
- inspect which triggers fired.

## 2. Action Review Workspace

This is the most important product surface after the Command Center.

Its job is to turn recommendations into accountable decisions.

### What The User Should See

Action list:

- action title;
- target;
- urgency;
- status;
- required reviewer role;
- short rationale.

Selected action detail:

- full rationale;
- triggering rules or triggers;
- knowledge bundle or policy source references;
- affected ward, room, or patient;
- operational constraints;
- expected timing;
- review controls.

### Required Review Controls

- approve;
- reject;
- defer;
- escalate;
- optional override reason.

### Suggested Interaction Pattern

Use a two-pane layout:

- left pane: action inbox;
- right pane: action detail and review panel.

This will feel efficient and credible in a demo.

## 3. Ward Detail View

This screen explains why a ward or unit is being prioritized.

### What The User Should See

- current ward risk level;
- vulnerability context;
- cluster or burden signals;
- relevant rooms;
- pending actions affecting that ward;
- recent event timeline;
- possible spread context.

### Recommended Elements

- ward header with risk badge and status;
- timeline of recent relevant events;
- room/bed or unit occupancy summary;
- vulnerability markers;
- action recommendations linked back to the ward;
- small evidence or trigger summary.

This screen is especially useful in the pitch because it makes the recommendation feel grounded in hospital reality.

## 4. System Context And Trace View

This can be either a separate screen or a slide-over panel.

For the hackathon, a drawer or side panel is probably better than a full separate page.

### Its Job

Show why the system produced what it produced.

### What The User Should See

- active knowledge bundle;
- deployment profile;
- fired trigger or rule ids;
- provenance or source references;
- current facts or contextual modifiers;
- audit trail for a selected action.

This is the trust surface.

## Recommended V1 Navigation

Keep navigation very small:

- `Command Center`
- `Actions`
- `Wards`
- `Trace`

Do not expose a large admin navigation yet.

## Recommended Screen Flow For The Demo

The strongest demo story is:

1. Open `Command Center`.
2. Show current influenza deployment state and hospital situation.
3. Trigger a run.
4. Show a high-priority action appearing in the action queue.
5. Open that action in the review workspace.
6. Show why it was recommended.
7. Open the related ward detail.
8. Submit a review decision.
9. Show the audit or trace panel.

That demonstrates:

- awareness;
- prioritization;
- reviewability;
- traceability.

## Recommended Data Surfaces For Each Screen

### Command Center

Should consume:

- `/health`
- `/api/v1/runs`
- `/api/v1/risk/alerts`
- `/api/v1/risk/assessments`
- `/api/v1/actions`

### Action Review Workspace

Should consume:

- `/api/v1/actions`
- `/api/v1/actions/{action_id}/review`
- `/api/v1/explainability/actions/{action_id}`

### Ward Detail View

Can start from:

- `/api/v1/state`
- `/api/v1/risk/assessments`
- `/api/v1/actions`

It will likely need more backend support later for cleaner ward-level aggregation.

### Trace View

Should consume:

- explainability data;
- action details;
- audit-linked references.

## Backend Gaps The Frontend Plan Reveals

The frontend can already be sketched now, but the plan reveals some backend gaps:

- no dedicated summary endpoint for dashboard counters;
- no dedicated ward-focused aggregation endpoint;
- no dedicated trigger trace endpoint for compiled runtime artifacts;
- the compiled source package is not yet the live runtime path;
- the explainability surface should become richer and more explicit.

These are good backend targets because they are product-facing.

## Visual Direction

The visual direction should feel like a clinical operations command surface, not a generic BI dashboard.

Recommended characteristics:

- light base, not dark-by-default;
- restrained but strong status colors;
- clear typography hierarchy;
- compact cards and panels;
- one strong accent for actionable items;
- alert states shown as operational severity, not decorative color noise.

Recommended color semantics:

- red: immediate operational risk;
- amber: caution or pending review;
- blue or teal: system and informational state;
- neutral slate: baseline structure.

## Interaction Style

Recommended interaction behavior:

- single-click access to the most urgent action;
- drawers or side panels for trace and explainability;
- minimal modal usage;
- explicit confirmation for review decisions;
- timelines and lists over complicated charts.

For this product, clarity beats novelty.

## What Not To Do In V1

Avoid:

- too many screens;
- a generic chatbot as the main UI;
- excessive map or graph visuals with weak operational meaning;
- buried review actions;
- over-dense tables without prioritization;
- a settings-heavy admin experience on the critical demo path.

## Recommended V1 MVP Screen Set

If implementation time is tight, build only these:

1. `Command Center`
2. `Action Review Workspace`
3. `Ward Detail Drawer`
4. `Trace Drawer`

This is enough to tell the whole story well.

## Recommended Next Frontend Planning Step

Before implementing the frontend, define:

- the exact fields shown in the dashboard summary band;
- the exact card shape for one proposed action;
- the exact detail layout for one ward;
- the exact trace payload needed from the backend.

That should become the first frontend contract.
