from app.core.config import VALID_PASSCODE, VALID_USERNAME
from app.models.auth import AuthRequest, AuthResponse


def authenticate(request: AuthRequest) -> AuthResponse:
    is_valid = (
        request.username == VALID_USERNAME and request.password == VALID_PASSCODE
    )
    message = "Authentication successful." if is_valid else "Invalid credentials."
    return AuthResponse(authenticated=is_valid, message=message)
