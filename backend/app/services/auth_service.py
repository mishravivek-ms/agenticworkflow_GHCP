from app.core.config import AUTH_PASSCODE, AUTH_USERNAME


def verify_credentials(username: str, passcode: str) -> bool:
    return username == AUTH_USERNAME and passcode == AUTH_PASSCODE
