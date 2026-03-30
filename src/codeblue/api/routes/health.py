from __future__ import annotations

from fastapi import APIRouter

from codeblue.settings import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def healthcheck() -> dict[str, str]:
    settings = get_settings()
    return {"status": "ok", "app": settings.app_name, "env": settings.env}
