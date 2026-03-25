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
