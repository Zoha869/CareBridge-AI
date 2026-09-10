"""
Application configuration module.

Centralizes all environment-based settings using Pydantic's BaseSettings.
This ensures every part of the application reads configuration from a
single, validated source instead of scattering os.getenv() calls
throughout the codebase.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Strongly-typed application settings, automatically loaded from
    environment variables (or a local .env file during development).
    """

    # General application metadata
    APP_NAME: str = "AI Patient-Doctor System"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    FRONTEND_URL: str = "http://localhost:5173"

    # Supabase project credentials
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_JWT_SECRET: str

    # Direct Postgres connection string (used by SQLAlchemy)
    DATABASE_URL: str
    GROQ_API_KEY: str

    # Pydantic-settings configuration: read values from a .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance so environment variables are
    parsed only once per application lifetime, instead of on every
    request.
    """
    return Settings()


# A ready-to-import settings instance for convenience.
settings = get_settings()
