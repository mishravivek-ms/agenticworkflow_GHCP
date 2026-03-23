import httpx

from app.core.config import settings
from app.models.auth import LoginRequest, LoginResponse


async def authenticate_user(payload: LoginRequest) -> LoginResponse:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.backend_base_url}/api/login",
                json=payload.model_dump(),
            )
    except httpx.RequestError:
        return LoginResponse(success=False, message="Backend unavailable")

    if response.status_code == httpx.codes.OK:
        return LoginResponse(**response.json())

    detail = response.json().get("detail", "Invalid credentials")
    return LoginResponse(success=False, message=detail)
