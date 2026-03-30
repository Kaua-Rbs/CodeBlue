from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from codeblue.api.routes.actions import router as actions_router
from codeblue.api.routes.events import router as events_router
from codeblue.api.routes.explainability import router as explainability_router
from codeblue.api.routes.health import router as health_router
from codeblue.api.routes.risk import router as risk_router
from codeblue.api.routes.runs import router as runs_router
from codeblue.api.routes.state import router as state_router
from codeblue.persistence.db import init_db
from codeblue.settings import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.include_router(health_router)
app.include_router(events_router, prefix=settings.api_prefix)
app.include_router(state_router, prefix=settings.api_prefix)
app.include_router(runs_router, prefix=settings.api_prefix)
app.include_router(risk_router, prefix=settings.api_prefix)
app.include_router(actions_router, prefix=settings.api_prefix)
app.include_router(explainability_router, prefix=settings.api_prefix)
