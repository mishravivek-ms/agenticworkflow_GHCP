"""
Application configuration using pydantic-settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "AgenticWorkflow API"
    APP_VERSION: str = "0.1.0"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8001"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
