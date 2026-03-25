# Project Plan: Basic Authentication Flow

## Overview

Build a simple web application with a username/password login screen backed by a FastAPI REST API.  
The frontend is rendered with **FastUI** (Python-based UI components served by FastAPI).  
Credentials are validated against hardcoded values on the backend — no external database is needed.

---

## Tech Stack

| Layer         | Technology          | Notes                              |
|---------------|---------------------|------------------------------------|
| Backend       | FastAPI (Python)    | REST API, serves FastUI pages      |
| Frontend      | FastUI              | UI components rendered via FastAPI |
| Package Mgr   | uv                  | Replaces pip/venv                  |
| Python        | 3.11+               | Minimum required version           |
| API Style     | REST                | JSON request/response              |

---

## Project Structure

```
auth-app/
├── pyproject.toml          # uv/PEP 517 project definition
├── uv.lock                 # Locked dependency graph (committed to VCS)
├── README.md
├── src/
│   └── auth_app/
│       ├── __init__.py
│       ├── main.py         # FastAPI application entry point
│       ├── routers/
│       │   ├── __init__.py
│       │   ├── auth.py     # /api/login REST endpoint
│       │   └── ui.py       # FastUI page routes (/, /login, /dashboard)
│       ├── models/
│       │   ├── __init__.py
│       │   └── auth.py     # Pydantic request/response models
│       └── core/
│           ├── __init__.py
│           └── security.py # Hardcoded credential validation logic
└── tests/
    ├── __init__.py
    ├── test_auth_api.py    # API-level tests (login success/failure)
    └── test_ui_routes.py   # FastUI route smoke tests
```

---

## Setup & Installation

### Prerequisites
- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

### Steps

```bash
# 1. Create and initialise the project with uv
uv init auth-app
cd auth-app

# 2. Add runtime dependencies
uv add fastapi fastui uvicorn

# 3. Add development/test dependencies
uv add --dev pytest httpx pytest-asyncio

# 4. Run the development server
uv run uvicorn src.auth_app.main:app --reload --port 8000

# 5. Run tests
uv run pytest
```

---

## Backend Implementation

### `pyproject.toml`

```toml
[project]
name = "auth-app"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.110.0",
    "fastui>=0.7.0",
    "uvicorn[standard]>=0.29.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "httpx>=0.27.0",
    "pytest-asyncio>=0.23.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

---

### `src/auth_app/core/security.py` — Credential Validation

```python
# Hardcoded credentials (replace with a real store in production)
VALID_USERNAME = "username"
VALID_PASSWORD = "passcode"


def validate_credentials(username: str, password: str) -> bool:
    """Return True only when username and password match the hardcoded values."""
    return username == VALID_USERNAME and password == VALID_PASSWORD
```

---

### `src/auth_app/models/auth.py` — Pydantic Models

```python
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    message: str
```

---

### `src/auth_app/routers/auth.py` — REST Endpoint

```python
from fastapi import APIRouter
from ..models.auth import LoginRequest, LoginResponse
from ..core.security import validate_credentials

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    """
    POST /api/login
    Body: { "username": "...", "password": "..." }
    Returns 200 with success=True on valid credentials,
    or 200 with success=False on invalid credentials.
    """
    ok = validate_credentials(payload.username, payload.password)
    if ok:
        return LoginResponse(success=True, message="Login successful")
    return LoginResponse(success=False, message="Invalid username or password")
```

> **Design decision:** HTTP 200 is returned in both cases so the FastUI frontend can read the JSON body without special error handling.  
> Optionally use HTTP 401 for failed attempts if a stricter API contract is preferred.

---

### `src/auth_app/routers/ui.py` — FastUI Pages

```python
from typing import Annotated
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastui import FastUI, AnyComponent, prebuilt_html
from fastui import components as c
from fastui.components.display import DisplayMode, DisplayLookup
from fastui.events import GoToEvent, PageEvent
from fastui.forms import fastui_form

from ..models.auth import LoginRequest

router = APIRouter(tags=["ui"])


@router.get("/", response_class=HTMLResponse)
async def root() -> HTMLResponse:
    """Redirect browser to /login."""
    return HTMLResponse('<meta http-equiv="refresh" content="0; url=/login">')


@router.get("/login", response_model=FastUI, response_model_exclude_none=True)
async def login_page() -> list[AnyComponent]:
    """Render the login form page."""
    return [
        c.Page(
            components=[
                c.Heading(text="Sign In", level=2),
                c.ModelForm(
                    model=LoginRequest,
                    submit_url="/api/login",
                    submit_trigger=PageEvent(name="login-submit"),
                    footer=[],
                    submit_on_change=False,
                ),
                c.Button(
                    text="Login",
                    on_click=PageEvent(name="login-submit"),
                ),
            ]
        )
    ]


@router.get("/dashboard", response_model=FastUI, response_model_exclude_none=True)
async def dashboard_page() -> list[AnyComponent]:
    """Protected dashboard page shown after successful login."""
    return [
        c.Page(
            components=[
                c.Heading(text="Welcome!", level=2),
                c.Paragraph(text="You are logged in successfully."),
                c.Link(
                    components=[c.Text(text="Logout")],
                    on_click=GoToEvent(url="/login"),
                ),
            ]
        )
    ]
```

---

### `src/auth_app/main.py` — Application Entry Point

```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastui import prebuilt_html

from .routers import auth, ui

app = FastAPI(title="Auth App")

# Mount routers
app.include_router(ui.router)
app.include_router(auth.router)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return HTMLResponse(status_code=204)


@app.get("/{path:path}", response_class=HTMLResponse, include_in_schema=False)
async def html_landing() -> HTMLResponse:
    """Serve the FastUI prebuilt HTML shell for all unmatched paths."""
    return HTMLResponse(prebuilt_html(title="Auth App"))
```

---

## Frontend Implementation (FastUI)

FastUI components are **Python objects** returned by FastAPI routes — no separate JavaScript project is needed.

### Login Screen (`/login`)

| Element      | FastUI Component | Details                                      |
|--------------|------------------|----------------------------------------------|
| Page title   | `c.Heading`      | "Sign In", level 2                           |
| Username     | `c.ModelForm`    | Auto-generated from `LoginRequest.username`  |
| Password     | `c.ModelForm`    | Auto-generated from `LoginRequest.password`  |
| Submit btn   | `c.Button`       | Triggers `PageEvent(name="login-submit")`    |
| Form action  | `submit_url`     | `POST /api/login`                            |

### Post-login Flow

1. FastUI sends `POST /api/login` with the form values.
2. Backend returns `{ "success": true/false, "message": "..." }`.
3. On success → redirect to `/dashboard`.  
4. On failure → display the `message` field as an inline error.

> **Note:** FastUI handles form submission and response automatically via its built-in JavaScript shell. Navigation on success is driven by returning a `GoToEvent` or a redirect in the API response.

---

## API Specification

### `POST /api/login`

**Request body (JSON):**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (success — 200):**
```json
{
  "success": true,
  "message": "Login successful"
}
```

**Response (failure — 200):**
```json
{
  "success": false,
  "message": "Invalid username or password"
}
```

**Hardcoded valid credentials:**
| Field     | Value      |
|-----------|------------|
| username  | `username` |
| password  | `passcode` |

---

## Testing Plan

### `tests/test_auth_api.py`

```python
import pytest
from httpx import AsyncClient, ASGITransport
from src.auth_app.main import app


@pytest.mark.asyncio
async def test_login_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/login", json={"username": "username", "password": "passcode"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "successful" in data["message"]


@pytest.mark.asyncio
async def test_login_wrong_password():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/login", json={"username": "username", "password": "wrong"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False


@pytest.mark.asyncio
async def test_login_wrong_username():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/login", json={"username": "admin", "password": "passcode"})
    assert response.status_code == 200
    assert response.json()["success"] is False


@pytest.mark.asyncio
async def test_login_missing_fields():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/login", json={})
    assert response.status_code == 422  # FastAPI validation error
```

### `tests/test_ui_routes.py`

```python
import pytest
from httpx import AsyncClient, ASGITransport
from src.auth_app.main import app


@pytest.mark.asyncio
async def test_login_page_returns_html():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/login", headers={"accept": "text/html"})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_dashboard_page_returns_fastui():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/dashboard", headers={"accept": "application/json"})
    assert response.status_code == 200
```

---

## Implementation Task Checklist

### Project Bootstrap
- [ ] Run `uv init auth-app` to scaffold the project
- [ ] Add runtime dependencies: `uv add fastapi fastui uvicorn`
- [ ] Add dev dependencies: `uv add --dev pytest httpx pytest-asyncio`
- [ ] Confirm `uv.lock` is generated and committed
- [ ] Create directory structure: `src/auth_app/{core,models,routers}` and `tests/`

### Backend
- [ ] Implement `src/auth_app/core/security.py` with `validate_credentials()`
- [ ] Implement `src/auth_app/models/auth.py` (`LoginRequest`, `LoginResponse`)
- [ ] Implement `src/auth_app/routers/auth.py` (`POST /api/login`)
- [ ] Implement `src/auth_app/routers/ui.py` (FastUI page routes)
- [ ] Implement `src/auth_app/main.py` (app factory, router mounting, HTML catch-all)

### Frontend (FastUI)
- [ ] Verify `/login` page renders a two-field form (username, password) and a submit button
- [ ] Verify successful login redirects to `/dashboard`
- [ ] Verify failed login shows an error message on the `/login` page
- [ ] Verify `/dashboard` shows a welcome message with a logout link

### Testing
- [ ] Write `tests/test_auth_api.py` covering success, wrong password, wrong username, missing fields
- [ ] Write `tests/test_ui_routes.py` covering HTML and FastUI route smoke tests
- [ ] Run full test suite: `uv run pytest` — all tests must pass

### Quality & Documentation
- [ ] Verify the app starts with `uv run uvicorn src.auth_app.main:app --reload`
- [ ] Manually test login with correct credentials (`username` / `passcode`)
- [ ] Manually test login with incorrect credentials
- [ ] Update `README.md` with setup and run instructions

---

## Security Notes

> These apply to a **production upgrade** of this prototype; they are out of scope for the initial implementation.

- Replace hardcoded credentials with a database lookup (e.g., SQLite via SQLAlchemy or SQLModel).
- Hash passwords with `bcrypt` or `argon2` — never compare plaintext passwords.
- Issue a signed JWT (or session cookie) on successful login instead of a JSON flag.
- Add rate limiting / account lockout to prevent brute-force attacks.
- Enforce HTTPS in production.
