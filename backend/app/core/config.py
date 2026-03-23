import os

from pydantic import BaseModel, Field


class Settings(BaseModel):
    auth_username: str = Field(default_factory=lambda: os.getenv("AUTH_USERNAME", "username"))
    auth_password: str = Field(default_factory=lambda: os.getenv("AUTH_PASSWORD", "passcode"))


settings = Settings()
