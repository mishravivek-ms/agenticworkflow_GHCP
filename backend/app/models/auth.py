from pydantic import BaseModel


class AuthRequest(BaseModel):
    username: str
    passcode: str


class AuthResponse(BaseModel):
    success: bool
    message: str
