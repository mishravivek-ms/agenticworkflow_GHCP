from fastapi import APIRouter, HTTPException, status

from app.models.auth import AuthRequest, AuthResponse
from app.services.auth_service import verify_credentials

router = APIRouter()


@router.post("/login", response_model=AuthResponse)
def login(payload: AuthRequest) -> AuthResponse:
    if verify_credentials(payload.username, payload.passcode):
        return AuthResponse(success=True, message="Authenticated")

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
    )
