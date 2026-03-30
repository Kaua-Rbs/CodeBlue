from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="CodeBlue")
    env: str = Field(default="development")
    api_prefix: str = Field(default="/api/v1")
    database_url: str = Field(default="sqlite+pysqlite:///./codeblue.db")
    sql_echo: bool = Field(default=False)

    model_config = SettingsConfigDict(
        env_prefix="CODEBLUE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
