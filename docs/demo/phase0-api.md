# Phase 0 API Walkthrough

Status: current
Scope: demo walkthrough for the current Phase 0 API slice
Last meaningful change: 2026-04-05

Purpose: give a concise operator-facing sequence for exercising the current backend demo through the API.

The current scaffold supports a thin end-to-end backend demo flow.

Suggested sequence:

1. Start the app.
2. `POST /api/v1/events` with the synthetic scenario payload.
3. `POST /api/v1/runs` to execute the demo pathogen and policy packs.
4. Inspect `GET /api/v1/state`.
5. Inspect `GET /api/v1/risk/assessments` and `GET /api/v1/risk/alerts`.
6. Inspect `GET /api/v1/actions`.
7. Submit a review decision with `POST /api/v1/actions/{action_id}/review`.
8. Inspect `GET /api/v1/explainability/actions/{action_id}`.

The sample payload lives at `seed/demo_scenarios/demo_outbreak.json`.

The repository now also contains a first real frontend scaffold under [frontend/](/home/kauar/CodeBlue/frontend). The easiest demo sequence is now:

1. start the FastAPI backend;
2. start the Vite frontend;
3. use `Load Demo Events` in the frontend;
4. trigger `Run Assessment`;
5. review the generated actions in the `Actions` workspace;
6. inspect the `Trace` drawer and `Wards` view.
