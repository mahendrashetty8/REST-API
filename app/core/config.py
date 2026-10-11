"""Application configuration settings."""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    PROJECT_NAME: str = "TaskFlow API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Reliable task management REST API"
    DATABASE_URL: str = "sqlite:///./taskflow.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
