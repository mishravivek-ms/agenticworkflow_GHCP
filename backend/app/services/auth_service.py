from app.core.config import settings


def authenticate_user(username: str, password: str) -> bool:
    return username == settings.auth_username and password == settings.auth_passcode
