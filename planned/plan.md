# Plan: Basic Authentication Flow

## Overview

Build a minimal full-stack web application with a login screen (FastUI frontend) and a REST
authentication endpoint (FastAPI backend). The backend validates credentials against a single
hard-coded user. The project is managed with **uv** and targets **Python 3.11+**.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Package manager | uv |
| Backend framework | FastAPI |
| Frontend framework | FastUI (served by FastAPI) |
| API style | REST (JSON) |
| Server | Uvicorn (ASGI) |

---

## Project Structure

```
agenticworkflow_GHCP/
├── planned/
│   └── plan.md               # this file
├── pyproject.toml            # uv project manifest
├── uv.lock                   # uv lock file (auto-generated)
├── README.md
└── app/
    ├── __init__.py
    ├── main.py               # FastAPI application entry-point
    ├── auth.py               # authentication logic
    └── frontend.py           # FastUI page definitions
```

---

## Task List

### 1. Project Initialisation

- [ ] **1.1** Initialise the project with `uv`:
  ```bash
  uv init --python 3.11
  ```
- [ ] **1.2** Add required dependencies via `uv add`:
  ```bash
  uv add fastapi "fastui" uvicorn
  ```
  Expected `pyproject.toml` dependencies block:
  ```toml
  [project]
  name = "agenticworkflow-ghcp"
  version = "0.1.0"
  requires-python = ">=3.11"
  dependencies = [
      "fastapi>=0.110.0",
      "fastui>=0.6.0",
      "uvicorn[standard]>=0.29.0",
  ]
  ```
- [ ] **1.3** Create the `app/` package directory with an empty `app/__init__.py`.

---

### 2. Backend – `app/auth.py`

Implement credential validation against a single hard-coded user.

- [ ] **2.1** Define the hard-coded credentials as module-level constants:
  ```python
  HARDCODED_USERNAME = "username"
  HARDCODED_PASSCODE = "passcode"
  ```
- [ ] **2.2** Create a Pydantic request model `LoginRequest`:
  ```python
  from pydantic import BaseModel

  class LoginRequest(BaseModel):
      username: str
      passcode: str
  ```
- [ ] **2.3** Create a Pydantic response model `LoginResponse`:
  ```python
  class LoginResponse(BaseModel):
      success: bool
      message: str
  ```
- [ ] **2.4** Implement the `authenticate(req: LoginRequest) -> LoginResponse` function that:
  - Returns `LoginResponse(success=True, message="Login successful")` when both fields match the constants.
  - Returns `LoginResponse(success=False, message="Invalid username or passcode")` otherwise.
  - Uses constant-time comparison (`secrets.compare_digest`) to avoid timing attacks.

---

### 3. Backend – `app/main.py`

Wire up the FastAPI app, REST endpoint, and FastUI static assets.

- [ ] **3.1** Create the FastAPI application instance:
  ```python
  from fastapi import FastAPI
  app = FastAPI(title="Auth Demo")
  ```
- [ ] **3.2** Mount the FastUI prebuilt static files so the browser can load the React bundle:
  ```python
  from fastui import prebuilt_html
  from fastapi.responses import HTMLResponse

  @app.get("/", response_class=HTMLResponse)
  async def root():
      return prebuilt_html(title="Login")
  ```
- [ ] **3.3** Register the FastUI API router (see Section 4) under the `/api` prefix:
  ```python
  from app.frontend import router as frontend_router
  app.include_router(frontend_router, prefix="/api")
  ```
- [ ] **3.4** Register the authentication REST endpoint `POST /auth/login`:
  ```python
  from app.auth import LoginRequest, LoginResponse, authenticate

  @app.post("/auth/login", response_model=LoginResponse)
  async def login(req: LoginRequest) -> LoginResponse:
      return authenticate(req)
  ```
- [ ] **3.5** Add a Uvicorn entry-point for local development at the bottom of the file:
  ```python
  if __name__ == "__main__":
      import uvicorn
      uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
  ```

---

### 4. Frontend – `app/frontend.py`

Build the FastUI login page. FastUI renders React components from Python objects and communicates
with the backend over the `/api` prefix.

- [ ] **4.1** Create an APIRouter for FastUI page routes:
  ```python
  from fastapi import APIRouter
  router = APIRouter()
  ```
- [ ] **4.2** Define the `/` page route that renders the login form:
  ```python
  from fastui import AnyComponent
  from fastui.components import Page, Heading, ModelForm
  from fastui.events import GoToEvent

  @router.get("/", response_model=list[AnyComponent])
  async def login_page() -> list[AnyComponent]:
      return [
          Page(
              components=[
                  Heading(text="Login", level=2),
                  ModelForm(
                      model=LoginFormModel,
                      submit_url="/auth/login",
                      submit_trigger=GoToEvent(url="/success"),
                  ),
              ]
          )
      ]
  ```
- [ ] **4.3** Define a Pydantic model `LoginFormModel` that FastUI uses to generate the form fields:
  ```python
  from pydantic import BaseModel, Field

  class LoginFormModel(BaseModel):
      username: str = Field(title="Username", description="Enter your username")
      passcode: str = Field(title="Passcode", description="Enter your passcode", json_schema_extra={"format": "password"})
  ```
- [ ] **4.4** Define a `/success` page route that is rendered after successful login:
  ```python
  @router.get("/success", response_model=list[AnyComponent])
  async def success_page() -> list[AnyComponent]:
      return [
          Page(
              components=[
                  Heading(text="Welcome!", level=2),
              ]
          )
      ]
  ```
- [ ] **4.5** Define a `/api/components` catch-all that FastUI requires to render non-matched routes gracefully (return 404 FastUI page or redirect to `/`).

---

### 5. REST API Contract

| Method | Path | Request body | Success response | Error response |
|---|---|---|---|---|
| `POST` | `/auth/login` | `{"username": "...", "passcode": "..."}` | `200 {"success": true, "message": "Login successful"}` | `200 {"success": false, "message": "Invalid username or passcode"}` |
| `GET` | `/` | — | HTML (FastUI shell) | — |
| `GET` | `/api/` | — | FastUI JSON components (login form) | — |
| `GET` | `/api/success` | — | FastUI JSON components (welcome page) | — |

> **Note:** Authentication failures return HTTP 200 with `success: false` rather than 401,
> to keep the FastUI `ModelForm` redirect flow simple. A production system should use 401 with
> proper session/token management.

---

### 6. Hard-coded Credentials (Backend)

| Field | Value |
|---|---|
| Username | `username` |
| Passcode | `passcode` |

These are defined as constants in `app/auth.py` and **must not** be moved to environment
variables or a database for this phase.

---

### 7. Running the Application

- [ ] **7.1** Document the run command in `README.md`:
  ```bash
  # Install dependencies
  uv sync

  # Start the development server
  uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
  ```
- [ ] **7.2** The login UI is available at `http://localhost:8000/`.
- [ ] **7.3** The REST endpoint is available at `http://localhost:8000/auth/login`.
- [ ] **7.4** The interactive API docs are at `http://localhost:8000/docs`.

---

### 8. Testing

- [ ] **8.1** Add `pytest` and `httpx` as dev dependencies:
  ```bash
  uv add --dev pytest httpx
  ```
- [ ] **8.2** Create `tests/__init__.py` (empty).
- [ ] **8.3** Create `tests/test_auth.py` with the following test cases:

  | Test name | Input | Expected |
  |---|---|---|
  | `test_login_success` | `{"username": "username", "passcode": "passcode"}` | `200`, `success=true` |
  | `test_login_wrong_password` | `{"username": "username", "passcode": "wrong"}` | `200`, `success=false` |
  | `test_login_wrong_username` | `{"username": "wrong", "passcode": "passcode"}` | `200`, `success=false` |
  | `test_login_both_wrong` | `{"username": "wrong", "passcode": "wrong"}` | `200`, `success=false` |
  | `test_login_empty_fields` | `{"username": "", "passcode": ""}` | `200`, `success=false` |

- [ ] **8.4** Use FastAPI's `TestClient` (backed by `httpx`) to exercise the `/auth/login` endpoint.
- [ ] **8.5** Run tests with:
  ```bash
  uv run pytest tests/ -v
  ```

---

### 9. UI/UX Requirements

- [ ] **9.1** The login screen must have:
  - A page heading "Login".
  - A "Username" text input field.
  - A "Passcode" password input field (characters masked).
  - A submit button labelled "Submit".
- [ ] **9.2** On successful login the user is redirected to the success page showing "Welcome!".
- [ ] **9.3** On failure the form should display an inline error message (FastUI handles this via
  the `ModelForm` error response from the server – the backend must return an HTTP 422 with a
  FastUI-compatible error payload when credentials are wrong, or the frontend must be configured
  to show a toast/alert).
- [ ] **9.4** The page must be responsive and render correctly on mobile viewport widths.

---

### 10. Security Considerations (Phase 1)

- [ ] **10.1** Use `secrets.compare_digest` in `app/auth.py` to prevent timing-based username
  or passcode enumeration.
- [ ] **10.2** The passcode field must be rendered as `type="password"` in the browser (masked).
- [ ] **10.3** Do **not** log the passcode value anywhere.
- [ ] **10.4** No session, token, or cookie is required for Phase 1.

---

### 11. Definition of Done

- [ ] `uv sync` completes without errors on a clean Python 3.11+ environment.
- [ ] `uv run uvicorn app.main:app --reload` starts without errors.
- [ ] Navigating to `http://localhost:8000/` shows the login form.
- [ ] Submitting `username` / `passcode` redirects to the success page.
- [ ] Submitting any other credentials stays on the login page and shows an error.
- [ ] All tests in `tests/test_auth.py` pass.
- [ ] `POST /auth/login` is documented in `/docs` (Swagger UI).
