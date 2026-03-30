# Phase 0 API Walkthrough

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
