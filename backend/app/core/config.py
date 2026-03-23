from pydantic import BaseModel


class Settings(BaseModel):
    auth_username: str = "username"
    auth_passcode: str = "passcode"


settings = Settings()
