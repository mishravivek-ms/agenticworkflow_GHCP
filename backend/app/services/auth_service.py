from app.core.config import EXPECTED_PASSCODE, EXPECTED_USERNAME
from app.models.auth import LoginRequest, LoginResponse


def authenticate(payload: LoginRequest) -> LoginResponse:
    is_valid = (
        payload.username == EXPECTED_USERNAME
        and payload.passcode == EXPECTED_PASSCODE
    )
    message = (
        "Authenticated successfully."
        if is_valid
        else "Invalid username or passcode."
    )
    return LoginResponse(authenticated=is_valid, message=message)
