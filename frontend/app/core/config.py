import os

from pydantic import BaseModel, Field


class Settings(BaseModel):
    backend_base_url: str = Field(
        default_factory=lambda: os.getenv("BACKEND_BASE_URL", "http://localhost:8000")
    )


settings = Settings()
