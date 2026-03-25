# Greenfield Project Plan: Basic Authentication Flow

## Overview

Build a simple authentication application with a FastUI frontend and FastAPI backend. The backend validates credentials against a hardcoded username and passcode. This plan is structured as a todo list of implementation tasks.

---

## Tech Stack

| Layer        | Technology          |
|--------------|---------------------|
| Frontend     | FastUI (Python)     |
| Backend      | FastAPI (Python)    |
| Package Mgr  | uv                  |
| Python       | 3.11+               |
| API Style    | REST                |
| Auth Storage | Hardcoded in-memory |

---

## Project Structure

```
auth-app/
├── pyproject.toml          # uv project manifest
├── uv.lock                 # uv lock file
├── README.md
├── src/
│   ├── main.py             # FastAPI app entry point (mounts both backend + FastUI)
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── router.py       # Auth REST endpoints (/api/login, /api/logout)
│   │   └── service.py      # Credential validation logic (hardcoded store)
│   └── ui/
│       ├── __init__.py
│       └── pages.py        # FastUI page definitions (login form, success page)
└── tests/
    ├── test_auth_router.py
    └── test_auth_service.py
```

---

## Todo List

### 1. Project Initialisation

- [ ] Initialise a new `uv` project: `uv init auth-app`
- [ ] Set Python version constraint to `>=3.11` in `pyproject.toml`
- [ ] Add runtime dependencies via uv:
  - `fastapi>=0.111`
  - `fastui>=0.7`
  - `uvicorn[standard]`
  - `python-multipart` (required for form data parsing)
- [ ] Add dev dependencies via uv:
  - `pytest`
  - `httpx` (async test client for FastAPI)
- [ ] Verify the virtual environment is created: `uv sync`

---

### 2. Backend – Credential Service (`src/auth/service.py`)

- [ ] Define a hardcoded credentials store:
  ```python
  HARDCODED_USERNAME = "username"
  HARDCODED_PASSCODE = "passcode"
  ```
- [ ] Implement `validate_credentials(username: str, password: str) -> bool` function that returns `True` only when both values match the hardcoded store exactly (case-sensitive).
- [ ] Ensure no credentials are ever logged or exposed in error messages.

---

### 3. Backend – Auth Router (`src/auth/router.py`)

- [ ] Create an `APIRouter` with prefix `/api`.
- [ ] Implement `POST /api/login` endpoint:
  - Accept JSON body: `{ "username": str, "password": str }`
  - Call `validate_credentials()`
  - On success → return `200 OK` with `{ "success": true, "message": "Login successful" }`
  - On failure → return `401 Unauthorized` with `{ "success": false, "message": "Invalid credentials" }`
- [ ] Implement `POST /api/logout` endpoint (stateless stub):
  - Return `200 OK` with `{ "message": "Logged out" }`
- [ ] Add appropriate Pydantic request/response models:
  - `LoginRequest(BaseModel)`: `username: str`, `password: str`
  - `LoginResponse(BaseModel)`: `success: bool`, `message: str`

---

### 4. Frontend – FastUI Pages (`src/ui/pages.py`)

- [ ] Create a FastUI `APIRouter` with prefix `/`.
- [ ] Implement `GET /` route → renders the **Login Page**:
  - Page title: `"Login"`
  - A `ModelForm` bound to the login form schema with fields:
    - `username` (text input, required, label `"Username"`)
    - `password` (password input, required, label `"Password"`)
  - Form `submit_url` pointing to `/api/login`
  - Display a generic error/success banner driven by query params (`?error=1`, `?success=1`)
- [ ] Implement `GET /dashboard` route → renders the **Dashboard / Success Page**:
  - Page title: `"Welcome"`
  - Display a `"Login successful – you are authenticated."` message component
  - A logout button/link that calls `POST /api/logout` and redirects to `/`
- [ ] Define FastUI form schema (`LoginForm`) using `pydantic` with the same fields as the `LoginRequest`.

---

### 5. Application Entry Point (`src/main.py`)

- [ ] Create a `FastAPI` application instance.
- [ ] Mount `fastui_serve` (FastUI static assets) at `/static`.
- [ ] Include the auth API router (prefix `/api`).
- [ ] Include the FastUI UI router (prefix `/`).
- [ ] Add a root redirect from `/` → login page via FastUI `prebuilt_html`.
- [ ] Configure `uvicorn` to run on `host="0.0.0.0"`, `port=8000`.
- [ ] Add an `if __name__ == "__main__"` guard to start uvicorn directly.

---

### 6. Tests (`tests/`)

- [ ] **`test_auth_service.py`**:
  - [ ] Test `validate_credentials` returns `True` for correct username + passcode.
  - [ ] Test `validate_credentials` returns `False` for wrong username.
  - [ ] Test `validate_credentials` returns `False` for wrong password.
  - [ ] Test `validate_credentials` returns `False` for empty strings.
  - [ ] Test `validate_credentials` is case-sensitive (e.g. `"Username"` ≠ `"username"`).

- [ ] **`test_auth_router.py`**:
  - [ ] Use `httpx.AsyncClient` + FastAPI `TestClient` / `ASGITransport`.
  - [ ] Test `POST /api/login` with valid credentials → `200` and `success: true`.
  - [ ] Test `POST /api/login` with invalid credentials → `401` and `success: false`.
  - [ ] Test `POST /api/login` with missing fields → `422 Unprocessable Entity`.
  - [ ] Test `POST /api/logout` → `200` with logout message.

---

### 7. Configuration & Documentation

- [ ] Add a `README.md` at project root covering:
  - [ ] Prerequisites (Python 3.11+, uv)
  - [ ] Installation steps (`uv sync`)
  - [ ] How to run the server (`uv run python src/main.py` or `uvicorn src.main:app --reload`)
  - [ ] How to run tests (`uv run pytest`)
  - [ ] Hardcoded credentials note (for development only)
- [ ] Add a `.gitignore` excluding `.venv/`, `__pycache__/`, `*.pyc`, `.env`, `uv.lock` (optional).
- [ ] Add `pyproject.toml` `[tool.pytest.ini_options]` section to configure test discovery (`testpaths = ["tests"]`).

---

### 8. Security Considerations (Dev Plan Notes)

- [ ] Document that hardcoded credentials are **for development/demo only**.
- [ ] Note the path to replace hardcoded store with a real database (e.g. SQLite + SQLModel) in a future iteration.
- [ ] Note that production auth should use hashed passwords (e.g. `bcrypt` via `passlib`) and JWT/session tokens.
- [ ] Note that HTTPS must be enforced in any production deployment.

---

## Acceptance Criteria

- [ ] Running `uv run python src/main.py` starts the server on `http://localhost:8000`.
- [ ] Navigating to `http://localhost:8000` shows the login form.
- [ ] Submitting `username` / `passcode` → redirects to `/dashboard` with success message.
- [ ] Submitting any other credentials → shows an error on the login page.
- [ ] All unit tests pass: `uv run pytest`.
- [ ] No credentials are hard-coded outside of `src/auth/service.py`.
