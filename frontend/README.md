# CodeBlue Frontend

This is the first real frontend scaffold for CodeBlue.

Current stack:

- React
- TypeScript
- Vite
- React Router
- TanStack Query
- Zustand
- CSS tokens plus CSS modules

## What It Already Does

- shows a real `Command Center`
- shows a real `Actions` workspace
- shows a real `Wards` view
- shows a global `Trace` drawer
- reads from the current FastAPI backend
- can load the demo event set into the backend
- can trigger a run
- can submit review decisions using the current review API

## Current Limitations

- it is only as complete as the current backend endpoints;
- some dashboard values are still derived client-side because summary endpoints do not exist yet;
- `defer` is present in the design spec but is not yet supported by the backend review API;
- ward views are assembled from current routes rather than a dedicated ward endpoint.

## Run Locally

From the repository root:

```bash
conda activate codeblue
uvicorn codeblue.api.main:app --reload
```

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies API requests to `http://127.0.0.1:8000`.
