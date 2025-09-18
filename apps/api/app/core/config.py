"""Configuration helpers for the Audiovook API."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    environment: str = Field(
        default="development", description="Current environment name"
    )
    debug: bool = Field(
        default=True, description="Enable debug mode during development"
    )
    database_url: str = Field(default="postgresql+asyncpg://avook:avook@db:5432/avook")
    redis_url: str = Field(default="redis://cache:6379/0")
    jwt_secret: str = Field(default="change-me")
    hmac_media_secret: str = Field(default="change-me-too")


@lru_cache
def get_settings() -> Settings:
    """Return a cached application settings instance."""

    return Settings()


__all__ = ["Settings", "get_settings"]
