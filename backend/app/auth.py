import hmac

VALID_USERNAME = "username"
VALID_PASSWORD = "passcode"


def authenticate(username: str, password: str) -> bool:
    """Return True only when both username and password are correct.

    Usernames are compared with a regular equality check (not a secret).
    Passwords are compared with hmac.compare_digest to prevent timing attacks.
    """
    username_match = username == VALID_USERNAME
    password_match = hmac.compare_digest(password, VALID_PASSWORD)
    return username_match and password_match
