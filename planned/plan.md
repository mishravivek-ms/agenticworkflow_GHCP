# Authentication Flow Implementation Plan

## Overview

Build a minimal full-stack authentication application with:
- **Backend**: FastAPI (Python 3.11+), managed with `uv`
- **Frontend**: FastUI (served by the FastAPI backend)
- **Authentication**: Hardcoded credentials check (`username` / `passcode`)
- **API Style**: REST

---

## Project Structure

```
agenticworkflow_GHCP/
├── planned/
│   └── plan.md                 # This file
├── backend/
│   ├── pyproject.toml          # uv project config & dependencies
│   ├── .python-version         # Pins Python 3.11
│   ├── main.py                 # FastAPI app entry point
│   ├── auth.py                 # Authentication logic
│   ├── models.py               # Pydantic request/response models
│   └── tests/
│       ├── __init__.py
│       └── test_auth.py        # Unit & integration tests
└── README.md
```

---

## Todo List

### 1. Project Bootstrap

- [ ] **1.1** Install `uv` (if not already available): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- [ ] **1.2** Initialise the backend project with uv:
  ```bash
  uv init backend
  cd backend
  ```
- [ ] **1.3** Set Python version to 3.11 in `backend/.python-version`:
  ```
  3.11
  ```
- [ ] **1.4** Add required dependencies via uv:
  ```bash
  uv add fastapi "fastui>=0.6.0" uvicorn python-multipart
  uv add --dev pytest httpx pytest-anyio
  ```
  The `pyproject.toml` `[project.dependencies]` section should contain:
  ```toml
  [project]
  name = "backend"
  version = "0.1.0"
  requires-python = ">=3.11"
  dependencies = [
      "fastapi>=0.110.0",
      "fastui>=0.6.0",
      "uvicorn[standard]>=0.29.0",
      "python-multipart>=0.0.9",
  ]

  [tool.uv]
  dev-dependencies = [
      "pytest>=8.0.0",
      "httpx>=0.27.0",
      "pytest-anyio>=0.0.0",
      "anyio[trio]>=4.3.0",
  ]
  ```

---

### 2. Backend — Authentication Logic (`auth.py`)

- [ ] **2.1** Create `backend/auth.py` with hardcoded credentials and a verification function:

  ```python
  # backend/auth.py

  HARDCODED_USERNAME = "username"
  HARDCODED_PASSWORD = "passcode"


  def verify_credentials(username: str, password: str) -> bool:
      """Return True only when both username and password match the hardcoded values."""
      return username == HARDCODED_USERNAME and password == HARDCODED_PASSWORD
  ```

  **Rules**:
  - Credentials are compared with plain equality (no hashing needed for this prototype).
  - The constants `HARDCODED_USERNAME` and `HARDCODED_PASSWORD` are defined at module level so they are easy to spot and replace later.

---

### 3. Backend — Pydantic Models (`models.py`)

- [ ] **3.1** Create `backend/models.py`:

  ```python
  # backend/models.py
  from pydantic import BaseModel


  class LoginRequest(BaseModel):
      username: str
      password: str


  class LoginResponse(BaseModel):
      success: bool
      message: str
  ```

---

### 4. Backend — FastAPI Application (`main.py`)

- [ ] **4.1** Create `backend/main.py` with:
  - A `GET /` route that serves the FastUI login page (HTML).
  - A `GET /api/` route that returns the FastUI page components (JSON) for the login form.
  - A `POST /api/login` REST endpoint that accepts `LoginRequest` JSON, calls `verify_credentials`, and returns `LoginResponse`.

  ```python
  # backend/main.py
  from fastapi import FastAPI
  from fastapi.responses import HTMLResponse
  from fastui import FastUI, AnyComponent, prebuilt_html
  from fastui import components as c
  from fastui.components.display import DisplayMode, DisplayLookup
  from fastui.events import GoToEvent, PageEvent
  from fastui.forms import fastui_form

  from models import LoginRequest, LoginResponse
  from auth import verify_credentials

  app = FastAPI(title="Auth Demo")


  # ── FastUI page ──────────────────────────────────────────────────────────────

  @app.get("/api/", response_model=FastUI, response_model_exclude_none=True)
  def login_page() -> list[AnyComponent]:
      """Return FastUI components that render the login form."""
      return [
          c.Page(
              components=[
                  c.Heading(text="Sign In", level=2),
                  c.ModelForm(
                      model=LoginRequest,
                      submit_url="/api/login",
                      submit_trigger=PageEvent(name="login-submit"),
                  ),
              ]
          )
      ]


  @app.get("/", response_class=HTMLResponse)
  async def root() -> HTMLResponse:
      """Serve the FastUI single-page shell."""
      return HTMLResponse(prebuilt_html(title="Login"))


  # ── REST login endpoint ───────────────────────────────────────────────────────

  @app.post("/api/login", response_model=LoginResponse)
  async def login(form: LoginRequest = fastui_form(LoginRequest)) -> LoginResponse:
      if verify_credentials(form.username, form.password):
          return LoginResponse(success=True, message="Login successful")
      return LoginResponse(success=False, message="Invalid username or password")
  ```

  **Key decisions**:
  - `GET /api/` returns the JSON component tree consumed by the FastUI JS shell.
  - `POST /api/login` is a standard REST endpoint; FastUI's `ModelForm` POSTs form-encoded data to this URL.
  - The endpoint uses `fastui_form()` to parse incoming form data into the `LoginRequest` model.

---

### 5. Frontend Details (FastUI)

FastUI renders the UI from JSON component descriptors served by the FastAPI backend — no separate frontend build step is required.

- [ ] **5.1** The login form is defined by `c.ModelForm(model=LoginRequest, submit_url="/api/login")`.
  - FastUI introspects `LoginRequest` and generates two text inputs: `username` and `password`.
  - The `password` field should be rendered as a password input. To achieve this, annotate the field in `LoginRequest`:
    ```python
    from pydantic import BaseModel, SecretStr

    class LoginRequest(BaseModel):
        username: str
        password: SecretStr   # FastUI renders SecretStr as <input type="password">
    ```
  - Update `verify_credentials` to unwrap the secret:
    ```python
    def verify_credentials(username: str, password: str) -> bool:
        return username == HARDCODED_USERNAME and password == HARDCODED_PASSWORD
    ```
    And in `main.py`, call:
    ```python
    verify_credentials(form.username, form.password.get_secret_value())
    ```

- [ ] **5.2** After a successful login the UI should show a success message. Use FastUI's `FireEvent` or redirect:
  ```python
  from fastui.events import GoToEvent
  # On success, redirect to /dashboard (even if it is a placeholder page)
  ```
  Alternatively, return a `c.Toast` or update the page components to show "Login successful".

- [ ] **5.3** On failure, the response JSON `{ "success": false, "message": "..." }` can be displayed using a `c.Text` component update — or simply rely on the browser to show the raw JSON for the prototype.

---

### 6. Running the Application

- [ ] **6.1** Start the server with uvicorn via uv:
  ```bash
  cd backend
  uv run uvicorn main:app --reload --port 8000
  ```
- [ ] **6.2** Open `http://localhost:8000` in a browser.
  - The login page renders automatically via FastUI.
  - Enter `username` / `passcode` to authenticate successfully.
  - Any other credentials return a failure message.

---

### 7. Tests (`backend/tests/test_auth.py`)

- [ ] **7.1** Create `backend/tests/__init__.py` (empty).
- [ ] **7.2** Create `backend/tests/test_auth.py`:

  ```python
  # backend/tests/test_auth.py
  import pytest
  from httpx import AsyncClient, ASGITransport

  # ── Unit tests for auth logic ─────────────────────────────────────────────────

  from auth import verify_credentials


  def test_valid_credentials():
      assert verify_credentials("username", "passcode") is True


  def test_wrong_password():
      assert verify_credentials("username", "wrong") is False


  def test_wrong_username():
      assert verify_credentials("wrong", "passcode") is False


  def test_empty_credentials():
      assert verify_credentials("", "") is False


  # ── Integration tests via HTTP ────────────────────────────────────────────────

  @pytest.mark.anyio
  async def test_login_success():
      from main import app
      async with AsyncClient(
          transport=ASGITransport(app=app), base_url="http://test"
      ) as client:
          resp = await client.post(
              "/api/login",
              data={"username": "username", "password": "passcode"},
          )
      assert resp.status_code == 200
      body = resp.json()
      assert body["success"] is True


  @pytest.mark.anyio
  async def test_login_failure():
      from main import app
      async with AsyncClient(
          transport=ASGITransport(app=app), base_url="http://test"
      ) as client:
          resp = await client.post(
              "/api/login",
              data={"username": "bad", "password": "bad"},
          )
      assert resp.status_code == 200
      body = resp.json()
      assert body["success"] is False


  @pytest.mark.anyio
  async def test_login_page_returns_components():
      from main import app
      async with AsyncClient(
          transport=ASGITransport(app=app), base_url="http://test"
      ) as client:
          resp = await client.get("/api/")
      assert resp.status_code == 200
      # FastUI returns a list of component dicts
      assert isinstance(resp.json(), list)
  ```

- [ ] **7.3** Add `pytest.ini` or `[tool.pytest.ini_options]` in `pyproject.toml`:
  ```toml
  [tool.pytest.ini_options]
  asyncio_mode = "auto"
  testpaths = ["tests"]
  ```
- [ ] **7.4** Run tests:
  ```bash
  cd backend
  uv run pytest
  ```

---

### 8. README Update

- [ ] **8.1** Update the top-level `README.md` with:
  - Project description
  - Prerequisites (Python 3.11+, uv)
  - Installation and run instructions
  - Default credentials (`username` / `passcode`)
  - How to run tests

---

## Acceptance Criteria

| # | Criterion |
|---|-----------|
| 1 | `GET /` returns an HTML page with a login form (username + password fields). |
| 2 | `POST /api/login` with `{"username":"username","password":"passcode"}` returns `{"success":true,"message":"Login successful"}`. |
| 3 | `POST /api/login` with wrong credentials returns `{"success":false,"message":"Invalid username or password"}`. |
| 4 | Password field is rendered as `<input type="password">` (masked input). |
| 5 | All unit and integration tests pass (`uv run pytest`). |
| 6 | Application starts with `uv run uvicorn main:app --reload`. |

---

## Out of Scope (for this iteration)

- Persistent user database or ORM
- JWT / session tokens
- Password hashing
- Registration / logout flows
- HTTPS / TLS configuration
- Docker / containerisation
