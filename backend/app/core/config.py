from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "CodeGuard AI"
    database_url: str = Field(default="postgresql+psycopg://postgres:codeguard-local@localhost:5432/codeguard")
    jwt_secret: str = Field(default="development-secret")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 30
    ai_api_key: str | None = None
    ai_model: str = "gpt-4o-mini"
    cors_origins: List[str] = ["http://localhost:3001"]
    max_file_size: int = 5 * 1024 * 1024
    analysis_timeout: int = 120

    @field_validator("database_url", mode="before")
    @classmethod
    def use_psycopg_driver(cls, value: str) -> str:
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value


settings = Settings()
