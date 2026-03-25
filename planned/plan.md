# Basic Authentication Flow — Implementation Plan

## Project Overview

Build a simple authentication application using **FastAPI** (backend) and **FastUI** (frontend) with **uv** as the Python package manager. The app presents a login form that accepts a username and password, then validates them against hardcoded credentials on the backend.

---

## Tech Stack

| Layer          | Technology       |
|----------------|-----------------|
| Backend        | FastAPI (Python) |
| Frontend       | FastUI           |
| Package Manager | uv              |
| Python Version | 3.11+           |
| API Style      | REST            |

---

## Todo List

### 1. Project Setup

- [ ] Initialise the project using `uv init auth-app`
- [ ] Set Python version to 3.11+ in `.python-version` or `pyproject.toml`
- [ ] Add dependencies via `uv add fastapi fastui uvicorn`
- [ ] Add dev dependencies via `uv add --dev pytest httpx`
- [ ] Define the project directory structure:
  ```
  auth-app/
  ├── pyproject.toml
  ├── .python-version
  ├── README.md
  ├── app/
  │   ├── __init__.py
  │   ├── main.py          # FastAPI app entry point
  │   ├── routers/
  │   │   ├── __init__.py
  │   │   └── auth.py      # Authentication endpoints
  │   ├── models/
  │   │   ├── __init__.py
  │   │   └── auth.py      # Pydantic request/response models
  │   ├── core/
  │   │   ├── __init__.py
  │   │   └── security.py  # Hardcoded credential validation logic
  │   └── ui/
  │       ├── __init__.py
  │       └── pages.py     # FastUI page definitions
  └── tests/
      ├── __init__.py
      ├── test_auth_api.py
      └── test_ui.py
  ```

---

### 2. Backend — FastAPI

#### 2a. Core Security Module (`app/core/security.py`)

- [ ] Define hardcoded credentials:
  ```python
  HARDCODED_USERNAME = "username"
  HARDCODED_PASSCODE = "passcode"
  ```
- [ ] Implement `verify_credentials(username: str, password: str) -> bool` function that performs a constant-time comparison using `secrets.compare_digest` to prevent timing attacks

#### 2b. Pydantic Models (`app/models/auth.py`)

- [ ] Create `LoginRequest` model with fields:
  - `username: str`
  - `password: str`
- [ ] Create `LoginResponse` model with fields:
  - `success: bool`
  - `message: str`

#### 2c. Authentication Router (`app/routers/auth.py`)

- [ ] Implement `POST /api/auth/login` endpoint:
  - Accepts `LoginRequest` body
  - Calls `verify_credentials()`
  - Returns `LoginResponse` with `success=True` and message `"Login successful"` on match
  - Returns HTTP 401 with message `"Invalid username or password"` on mismatch
- [ ] Implement `GET /api/auth/logout` endpoint (placeholder, returns success message)

#### 2d. FastAPI App Entry Point (`app/main.py`)

- [ ] Create the FastAPI application instance with title and description
- [ ] Mount the FastUI static assets
- [ ] Include the authentication router under `/api` prefix
- [ ] Add a root route that serves the FastUI login page
- [ ] Configure CORS middleware (allow localhost for development)

---

### 3. Frontend — FastUI

#### 3a. Login Page (`app/ui/pages.py`)

- [ ] Define a FastUI `Page` component for the login screen with:
  - Application title / heading (`"Login"`)
  - A `Form` component with:
    - `username` input field (type: text, label: "Username", required)
    - `password` input field (type: password, label: "Password", required)
    - Submit button labelled `"Sign In"`
  - Form action pointing to `POST /api/auth/login`
- [ ] Define a success page displayed after a successful login
- [ ] Define an error component shown inline when login fails (invalid credentials)

#### 3b. FastUI Route (`app/main.py`)

- [ ] Add `GET /` route that returns the FastUI login page definition as JSON (FastUI renders it client-side)
- [ ] Add `GET /success` route that returns the FastUI success page after login

---

### 4. API Design

| Method | Path                  | Description                       |
|--------|-----------------------|-----------------------------------|
| GET    | `/`                   | Serve FastUI login page           |
| GET    | `/success`            | Serve FastUI success page         |
| POST   | `/api/auth/login`     | Validate credentials, return result |
| GET    | `/api/auth/logout`    | Logout placeholder                |
| GET    | `/docs`               | FastAPI auto-generated Swagger UI |

**Request body for `POST /api/auth/login`:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Success response (HTTP 200):**
```json
{
  "success": true,
  "message": "Login successful"
}
```

**Failure response (HTTP 401):**
```json
{
  "detail": "Invalid username or password"
}
```

---

### 5. Testing

- [ ] Write unit tests for `verify_credentials()` in `tests/test_auth_api.py`:
  - Test correct username and password returns `True`
  - Test wrong password returns `False`
  - Test wrong username returns `False`
  - Test empty credentials returns `False`
- [ ] Write integration tests for `POST /api/auth/login` using FastAPI `TestClient`:
  - Valid credentials → HTTP 200 with `success: true`
  - Invalid password → HTTP 401
  - Invalid username → HTTP 401
  - Missing fields → HTTP 422 (validation error)
- [ ] Write smoke tests to verify the FastUI pages render without errors
- [ ] Run all tests with `uv run pytest`

---

### 6. Developer Experience

- [ ] Add a `Makefile` or `justfile` with common commands:
  - `make run` → `uv run uvicorn app.main:app --reload`
  - `make test` → `uv run pytest`
  - `make lint` → `uv run ruff check .`
- [ ] Add `ruff` as a dev dependency for linting: `uv add --dev ruff`
- [ ] Add a `.gitignore` for Python projects (exclude `__pycache__`, `.venv`, `dist`, etc.)
- [ ] Write a `README.md` with setup and usage instructions

---

### 7. Security Considerations

- [ ] Use `secrets.compare_digest` for credential comparison to prevent timing attacks
- [ ] Ensure passwords are never logged
- [ ] Add rate-limiting note for future production hardening (e.g., `slowapi`)
- [ ] Document that hardcoded credentials are for demo only and must be replaced with a database + hashed passwords for production

---

## Acceptance Criteria

- [ ] Running `uv run uvicorn app.main:app --reload` starts the server on `http://localhost:8000`
- [ ] Navigating to `http://localhost:8000` shows the FastUI login page with username and password fields
- [ ] Submitting `username` / `passcode` redirects to the success page
- [ ] Submitting any other credentials shows an error message
- [ ] All unit and integration tests pass
- [ ] The FastAPI `/docs` Swagger UI is accessible and documents all endpoints
