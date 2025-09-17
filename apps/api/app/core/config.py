"""Configuration helpers for the Audiovook API."""

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    debug: bool = Field(default=True, description="Enable debug mode during development")
    database_url: str = Field(default="postgresql+asyncpg://avook:avook@db:5432/avook")
    redis_url: str = Field(default="redis://cache:6379/0")
    jwt_secret: str = Field(default="change-me")
    hmac_media_secret: str = Field(default="change-me-too")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    """Return application settings instance."""

    return Settings()
