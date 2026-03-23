# Basic Authentication Flow — Implementation Plan

## Overview

Build a minimal authentication application with a FastUI frontend and a FastAPI
backend.  The user enters a username and passcode in the UI; the backend checks
the credentials against hardcoded values and returns a success or failure
response.

**Tech stack**

| Layer | Technology |
|-------|------------|
| Backend | FastAPI (Python ≥ 3.11) |
| Frontend | FastUI (served via FastAPI) |
| Package manager | uv |
| API style | REST (JSON) |

---

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI application entry-point
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── config.py      # Hardcoded credentials / env-var overrides
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── auth.py        # Pydantic request/response models
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   └── auth.py        # POST /auth/login endpoint
│   │   └── services/
│   │       ├── __init__.py
│   │       └── auth_service.py  # Authentication business logic
│   ├── pyproject.toml
│   └── README.md
├── frontend/
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py            # FastUI application (login form + result page)
│   ├── pyproject.toml
│   └── README.md
├── planned/
│   └── plan.md                # This file
└── README.md
```

---

## Todo List

### 1. Repository & Tooling Setup

- [x] Initialise Git repository
- [x] Add `.gitignore` (Python, uv artefacts)
- [x] Create root `README.md` with project overview and quick-start guide
- [x] Choose `uv` as the package manager for both sub-projects

---

### 2. Backend — FastAPI

#### 2.1 Project Bootstrap

- [x] Create `backend/pyproject.toml`
  - `requires-python = ">=3.11"`
  - Dependencies: `fastapi`, `uvicorn`, `pydantic`
  - Build backend: `hatchling`
- [x] Create `backend/app/__init__.py`

#### 2.2 Configuration (`backend/app/core/config.py`)

- [x] Define `VALID_USERNAME` (default `"username"`) loaded from environment
  variable `VALID_USERNAME`
- [x] Define `VALID_PASSCODE` (default `"passcode"`) loaded from environment
  variable `VALID_PASSCODE`
- [x] Emit a `RuntimeWarning` when default credentials are used (development
  safety hint)

#### 2.3 Data Models (`backend/app/models/auth.py`)

- [x] `AuthRequest` Pydantic model
  - `username: str` (min length 1)
  - `passcode: str` (min length 1)
- [x] `AuthResponse` Pydantic model
  - `authenticated: bool`
  - `message: str`

#### 2.4 Authentication Service (`backend/app/services/auth_service.py`)

- [x] `authenticate(request: AuthRequest) -> AuthResponse` function
  - Use `secrets.compare_digest` for timing-safe comparison of both fields
  - Return `AuthResponse(authenticated=True, message="Authentication successful.")`
    on match
  - Return `AuthResponse(authenticated=False, message="Invalid credentials.")`
    on mismatch

#### 2.5 Router (`backend/app/routers/auth.py`)

- [x] `POST /auth/login`
  - Accept JSON body matching `AuthRequest`
  - Call `authenticate()`
  - Return `200 OK` with `AuthResponse` on success
  - Return `401 Unauthorized` with `AuthResponse` on failure

#### 2.6 Application Entry-Point (`backend/app/main.py`)

- [x] Create `FastAPI` app titled `"Authentication API"`
- [x] Register the auth router (prefix `/auth`)
- [x] Add `GET /health` → `{"status": "ok"}` for liveness checks

#### 2.7 Backend README (`backend/README.md`)

- [x] Setup instructions (`uv venv`, `uv pip install -e .`)
- [x] Run command (`uvicorn app.main:app --reload --port 8000`)
- [x] Configuration section (env vars)
- [x] Example `curl` command

---

### 3. Frontend — FastUI

#### 3.1 Project Bootstrap

- [x] Create `frontend/pyproject.toml`
  - `requires-python = ">=3.11"`
  - Dependencies: `fastapi`, `fastui`, `httpx`, `pydantic`,
    `python-multipart`, `uvicorn`
  - Build backend: `hatchling`
- [x] Create `frontend/app/__init__.py`

#### 3.2 Application (`frontend/app/main.py`)

- [x] Read `BACKEND_URL` from environment (default `http://localhost:8000`)
- [x] Read `BACKEND_TIMEOUT_SECONDS` from environment (default `5.0`)
- [x] `GET /` → serve prebuilt FastUI HTML shell
- [x] `GET /api` → return `login_page()` FastUI component tree
- [x] `POST /api/login` (form submission)
  - Forward credentials as JSON to `{BACKEND_URL}/auth/login` via `httpx`
  - On network error → show failure result page
  - On HTTP 4xx/5xx → parse JSON body and show result page
  - On success → show result page with `"Authentication successful."` message
- [x] `login_page()` helper — renders
  - `Heading` "Sign in"
  - Optional status `Text` (for error messages passed back)
  - `Form` with fields `username` (text) and `passcode` (password), submit
    button "Sign in"
- [x] `result_page(message, authenticated)` helper — renders
  - `Heading` "Login Success" or "Login Failed"
  - `Text` with the message
  - `Button` "Back to form" linking to `/`

#### 3.3 Frontend README (`frontend/README.md`)

- [x] Setup instructions
- [x] Run command (`uvicorn app.main:app --reload --port 8001`)
- [x] Note about `BACKEND_URL` env var

---

### 4. Integration & Manual Testing

- [ ] Start the backend on port 8000
- [ ] Start the frontend on port 8001
- [ ] Open `http://localhost:8001` and verify the login form renders
- [ ] Submit correct credentials (`username` / `passcode`) → verify success page
- [ ] Submit wrong credentials → verify failure page
- [ ] Verify `GET http://localhost:8000/health` returns `{"status": "ok"}`
- [ ] Verify `POST http://localhost:8000/auth/login` with correct JSON returns
  `200` and `{"authenticated": true, …}`
- [ ] Verify `POST http://localhost:8000/auth/login` with wrong credentials
  returns `401` and `{"authenticated": false, …}`

---

### 5. Optional Enhancements (out of scope for MVP)

- [ ] Add automated unit tests for `authenticate()` (pytest)
- [ ] Add automated integration tests for the `/auth/login` endpoint (httpx
  test client)
- [ ] Containerise both services with Docker / Docker Compose
- [ ] Replace hardcoded credentials with a database user store
- [ ] Add JWT token issuance on successful login
- [ ] Add HTTPS / TLS termination

---

## API Contract

### `POST /auth/login`

**Request**

```json
{
  "username": "username",
  "passcode": "passcode"
}
```

**Response — 200 OK (success)**

```json
{
  "authenticated": true,
  "message": "Authentication successful."
}
```

**Response — 401 Unauthorized (failure)**

```json
{
  "authenticated": false,
  "message": "Invalid credentials."
}
```

---

## Running the Project

```bash
# Terminal 1 — Backend
cd backend
uv venv
source .venv/bin/activate
uv pip install -e .
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
uv venv
source .venv/bin/activate
uv pip install -e .
export BACKEND_URL="http://localhost:8000"
uvicorn app.main:app --reload --port 8001
```

Visit `http://localhost:8001` to use the login UI.
