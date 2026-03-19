import secrets

from app.core.config import VALID_PASSCODE, VALID_USERNAME
from app.models.auth import AuthRequest, AuthResponse


def authenticate(request: AuthRequest) -> AuthResponse:
    username_valid = secrets.compare_digest(request.username, VALID_USERNAME)
    passcode_valid = secrets.compare_digest(request.passcode, VALID_PASSCODE)
    is_valid = username_valid and passcode_valid
    message = "Authentication successful." if is_valid else "Invalid credentials."
    return AuthResponse(authenticated=is_valid, message=message)
