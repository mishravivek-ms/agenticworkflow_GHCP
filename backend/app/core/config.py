import os

from pydantic import BaseModel

AUTH_USERNAME = os.getenv("AUTH_USERNAME", "username")
AUTH_PASSWORD = os.getenv("AUTH_PASSWORD", "passcode")


class Settings(BaseModel):
    auth_username: str = AUTH_USERNAME
    auth_password: str = AUTH_PASSWORD


settings = Settings()
