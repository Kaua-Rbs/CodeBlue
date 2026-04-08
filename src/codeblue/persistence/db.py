from __future__ import annotations

from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from codeblue.persistence.orm_models import Base
from codeblue.settings import get_settings


def _engine_kwargs(database_url: str, sql_echo: bool) -> dict[str, Any]:
    kwargs: dict[str, Any] = {"echo": sql_echo}
    if database_url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    return kwargs


settings = get_settings()
engine = create_engine(
    settings.database_url, **_engine_kwargs(settings.database_url, settings.sql_echo)
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
