import pytest
from fastapi.testclient import TestClient

from app.auth import authenticate
from app.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Unit tests for authenticate()
# ---------------------------------------------------------------------------

def test_authenticate_correct_credentials():
    assert authenticate("username", "passcode") is True


def test_authenticate_wrong_username():
    assert authenticate("wrong_user", "passcode") is False


def test_authenticate_wrong_password():
    assert authenticate("username", "wrong_pass") is False


def test_authenticate_both_wrong():
    assert authenticate("wrong_user", "wrong_pass") is False


# ---------------------------------------------------------------------------
# Integration tests for POST /api/login
# ---------------------------------------------------------------------------

def test_login_valid_credentials():
    response = client.post("/api/login", json={"username": "username", "password": "passcode"})
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Login successful"


def test_login_invalid_credentials():
    response = client.post("/api/login", json={"username": "bad", "password": "bad"})
    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Invalid username or password"


def test_login_invalid_password_only():
    response = client.post("/api/login", json={"username": "username", "password": "wrong"})
    assert response.status_code == 401
    assert response.json()["success"] is False


def test_login_missing_fields():
    response = client.post("/api/login", json={"username": "username"})
    assert response.status_code == 422
