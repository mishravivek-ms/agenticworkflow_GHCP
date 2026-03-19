from fastapi import APIRouter

from app.models.auth import LoginRequest, LoginResponse
from app.services.auth_service import authenticate

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    return authenticate(payload)
