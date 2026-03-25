import hmac

# MVP credentials — hardcoded for the MVP only.
# WARNING: Production deployments MUST replace these with a proper user store
# (e.g., PostgreSQL) and use a password-hashing algorithm such as bcrypt or
# argon2 to store and verify passwords.  `hmac.compare_digest` prevents
# timing-based attacks but does NOT hash the password.
VALID_USERNAME = "username"
VALID_PASSWORD = "passcode"


def authenticate(username: str, password: str) -> bool:
    """Return True only when both username and password match the stored credentials.

    Usernames are compared with a plain equality check (they are not secret).
    Passwords are compared with :func:`hmac.compare_digest` to prevent
    timing-based side-channel attacks.
    """
    username_ok = username == VALID_USERNAME
    password_ok = hmac.compare_digest(password, VALID_PASSWORD)
    return username_ok and password_ok
