from fastapi import APIRouter, status

from app.models.auth import AuthRequest, AuthResponse
from app.services.auth_service import authenticate

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=AuthResponse, status_code=status.HTTP_200_OK)
def login(request: AuthRequest) -> AuthResponse:
    return authenticate(request)
