from pydantic import BaseModel


class Settings(BaseModel):
    backend_base_url: str = "http://localhost:8000"


settings = Settings()
