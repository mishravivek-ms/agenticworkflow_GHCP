"""Tests for Pydantic request/response models (LoginRequest, LoginResponse)."""
import pytest
from pydantic import ValidationError

from app.models import LoginRequest, LoginResponse


# ---------------------------------------------------------------------------
# LoginRequest
# ---------------------------------------------------------------------------


class TestLoginRequest:
    def test_valid_construction(self):
        req = LoginRequest(username="alice", password="secret")
        assert req.username == "alice"
        assert req.password == "secret"

    def test_missing_username_raises(self):
        with pytest.raises(ValidationError):
            LoginRequest(password="secret")

    def test_missing_password_raises(self):
        with pytest.raises(ValidationError):
            LoginRequest(username="alice")

    def test_missing_both_fields_raises(self):
        with pytest.raises(ValidationError):
            LoginRequest()

    def test_empty_strings_are_accepted(self):
        # Pydantic accepts empty strings for str fields; auth logic rejects them
        req = LoginRequest(username="", password="")
        assert req.username == ""
        assert req.password == ""

    def test_whitespace_strings_are_accepted(self):
        req = LoginRequest(username="  ", password="  ")
        assert req.username == "  "

    def test_non_string_username_raises(self):
        # Pydantic v2 strict str type rejects non-string input
        with pytest.raises(ValidationError):
            LoginRequest(username=42, password="pw")

    def test_serialisation_to_dict(self):
        req = LoginRequest(username="bob", password="pass123")
        data = req.model_dump()
        assert data == {"username": "bob", "password": "pass123"}

    def test_serialisation_to_json(self):
        req = LoginRequest(username="carol", password="qwerty")
        json_str = req.model_dump_json()
        assert '"username":"carol"' in json_str
        assert '"password":"qwerty"' in json_str

    def test_extra_fields_ignored(self):
        # By default Pydantic ignores extra fields; ensure no error is raised
        req = LoginRequest(username="dave", password="pw", role="admin")
        assert req.username == "dave"


# ---------------------------------------------------------------------------
# LoginResponse
# ---------------------------------------------------------------------------


class TestLoginResponse:
    def test_success_response(self):
        resp = LoginResponse(success=True, message="Login successful")
        assert resp.success is True
        assert resp.message == "Login successful"

    def test_failure_response(self):
        resp = LoginResponse(success=False, message="Invalid username or password")
        assert resp.success is False
        assert resp.message == "Invalid username or password"

    def test_missing_success_raises(self):
        with pytest.raises(ValidationError):
            LoginResponse(message="ok")

    def test_missing_message_raises(self):
        with pytest.raises(ValidationError):
            LoginResponse(success=True)

    def test_missing_both_fields_raises(self):
        with pytest.raises(ValidationError):
            LoginResponse()

    def test_serialisation_to_dict_success(self):
        resp = LoginResponse(success=True, message="Login successful")
        data = resp.model_dump()
        assert data == {"success": True, "message": "Login successful"}

    def test_serialisation_to_dict_failure(self):
        resp = LoginResponse(success=False, message="Invalid username or password")
        data = resp.model_dump()
        assert data == {"success": False, "message": "Invalid username or password"}

    def test_bool_field_type(self):
        resp = LoginResponse(success=True, message="ok")
        assert isinstance(resp.success, bool)

    def test_message_field_type(self):
        resp = LoginResponse(success=False, message="err")
        assert isinstance(resp.message, str)
