from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., examples=["username"])
    passcode: str = Field(..., examples=["passcode"])


class LoginResponse(BaseModel):
    authenticated: bool
    message: str
