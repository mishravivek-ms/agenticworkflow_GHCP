import logging

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
    except httpx.RequestError as exc:
        logging.getLogger(__name__).exception("Failed to reach backend", exc_info=exc)
        return LoginResponse(success=False, message="Backend unavailable")

    try:
        data = response.json()
    except ValueError:
        return LoginResponse(success=False, message="Unexpected response from backend")

    if response.is_success:
        if isinstance(data, dict):
            return LoginResponse(**data)
        return LoginResponse(success=True, message="Authenticated")

    detail = data.get("detail", "Invalid credentials") if isinstance(data, dict) else "Invalid credentials"
    return LoginResponse(success=False, message=detail)
