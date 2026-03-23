import secrets

from app.core.config import settings


def authenticate_user(username: str, password: str) -> bool:
    username_matches = secrets.compare_digest(username, settings.auth_username)
    password_matches = secrets.compare_digest(password, settings.auth_password)
    return username_matches and password_matches
