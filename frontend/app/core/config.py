import os

from pydantic import BaseModel

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")


class Settings(BaseModel):
    backend_base_url: str = BACKEND_BASE_URL


settings = Settings()
