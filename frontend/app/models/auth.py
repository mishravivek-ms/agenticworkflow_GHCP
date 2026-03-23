from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, title="Username")
    password: str = Field(
        ...,
        min_length=1,
        title="Password",
        json_schema_extra={"format": "password"},
    )


class LoginResponse(BaseModel):
    success: bool
    message: str
