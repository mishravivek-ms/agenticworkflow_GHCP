"""Tests for the authentication logic and /api/login endpoint."""
import pytest
from fastapi.testclient import TestClient

from app.auth import authenticate
from app.main import app

client = TestClient(app)

# ---------------------------------------------------------------------------
# Unit tests – authenticate()
# ---------------------------------------------------------------------------


def test_authenticate_correct_credentials():
    assert authenticate("username", "passcode") is True


def test_authenticate_wrong_username():
    assert authenticate("wronguser", "passcode") is False


def test_authenticate_wrong_password():
    assert authenticate("username", "wrongpass") is False


def test_authenticate_both_wrong():
    assert authenticate("wronguser", "wrongpass") is False


def test_authenticate_empty_credentials():
    assert authenticate("", "") is False


# ---------------------------------------------------------------------------
# Integration tests – POST /api/login
# ---------------------------------------------------------------------------


def test_login_valid_credentials_returns_200():
    response = client.post(
        "/api/login",
        json={"username": "username", "password": "passcode"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Login successful"


def test_login_invalid_credentials_returns_401():
    response = client.post(
        "/api/login",
        json={"username": "username", "password": "wrong"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["message"] == "Invalid username or password"


def test_login_wrong_username_returns_401():
    response = client.post(
        "/api/login",
        json={"username": "notauser", "password": "passcode"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False


def test_login_missing_fields_returns_422():
    response = client.post("/api/login", json={"username": "username"})
    assert response.status_code == 422


def test_login_empty_body_returns_422():
    response = client.post("/api/login", json={})
    assert response.status_code == 422


def test_login_response_has_success_key():
    response = client.post(
        "/api/login",
        json={"username": "username", "password": "passcode"},
    )
    assert "success" in response.json()


def test_login_response_has_message_key():
    response = client.post(
        "/api/login",
        json={"username": "username", "password": "passcode"},
    )
    assert "message" in response.json()


def test_login_success_message_text():
    response = client.post(
        "/api/login",
        json={"username": "username", "password": "passcode"},
    )
    assert response.json()["message"] == "Login successful"


def test_login_failure_message_text():
    response = client.post(
        "/api/login",
        json={"username": "username", "password": "bad"},
    )
    assert response.json()["message"] == "Invalid username or password"


def test_login_case_sensitive_username():
    response = client.post(
        "/api/login",
        json={"username": "Username", "password": "passcode"},
    )
    assert response.status_code == 401


def test_login_case_sensitive_password():
    response = client.post(
        "/api/login",
        json={"username": "username", "password": "Passcode"},
    )
    assert response.status_code == 401


def test_login_whitespace_credentials():
    response = client.post(
        "/api/login",
        json={"username": " username", "password": "passcode"},
    )
    assert response.status_code == 401


def test_login_extra_fields_ignored():
    response = client.post(
        "/api/login",
        json={"username": "username", "password": "passcode", "role": "admin"},
    )
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Unit tests – authenticate() edge cases
# ---------------------------------------------------------------------------


def test_authenticate_case_sensitive_username():
    assert authenticate("Username", "passcode") is False


def test_authenticate_case_sensitive_password():
    assert authenticate("username", "Passcode") is False


def test_authenticate_leading_whitespace():
    assert authenticate(" username", "passcode") is False


def test_authenticate_trailing_whitespace():
    assert authenticate("username ", "passcode") is False


def test_authenticate_returns_bool_type():
    result = authenticate("username", "passcode")
    assert isinstance(result, bool)


def test_authenticate_special_characters():
    assert authenticate("user@name!", "p@ss#word") is False


def test_authenticate_sql_injection_like_input():
    assert authenticate("' OR '1'='1", "' OR '1'='1") is False
