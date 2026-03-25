# Project Plan: Basic Authentication Flow

## Overview
Build a new project with a basic authentication flow using FastAPI (backend) and FastUI (frontend), managed with `uv` and targeting Python 3.11+..

---

## Tech Stack

| Layer         | Technology        |
|---------------|-------------------|
| Backend       | FastAPI (Python)  |
| Frontend      | FastUI            |
| Package Mgr   | uv                |
| Python        | 3.11+             |
| API Style     | REST              |
| Data Store    | Hardcoded in-memory (no database for MVP) |

---

## Todo List

### Project Setup
- [ ] Initialise project with `uv init` (creates `pyproject.toml` + virtual environment)
- [ ] Add runtime dependencies via `uv add fastapi fastui uvicorn`
- [ ] Add dev dependencies via `uv add --dev pytest httpx`
- [ ] Create the following directory layout:
  ```
  project-root/
  ├── pyproject.toml
  ├── uv.lock
  ├── README.md
  ├── app/
  │   ├── __init__.py
  │   ├── main.py          # FastAPI application entry point
  │   ├── auth.py          # Authentication logic
  │   ├── models.py        # Pydantic request/response models
  │   └── ui.py            # FastUI page definitions
  └── tests/
      ├── __init__.py
      └── test_auth.py
  ```

---

### Backend – FastAPI

#### `app/models.py`
- [ ] Define `LoginRequest` Pydantic model with fields:
  - `username: str`
  - `password: str`
- [ ] Define `LoginResponse` Pydantic model with fields:
  - `success: bool`
  - `message: str`

#### `app/auth.py`
- [ ] Hardcode credentials:
  ```python
  VALID_USERNAME = "username"
  VALID_PASSWORD = "passcode"
  ```
- [ ] Implement `authenticate(username: str, password: str) -> bool` function:
  - Compare `username` with a regular equality check (usernames are not secret)
  - Compare `password` using `hmac.compare_digest` to avoid timing-based attacks

#### `app/main.py`
- [ ] Create `FastAPI` app instance
- [ ] Mount the FastUI static assets (required for the browser UI)
- [ ] `POST /api/login` endpoint:
  - Accepts `LoginRequest` body (JSON)
  - Calls `authenticate()` from `auth.py`
  - Returns `LoginResponse` with `success=True/False` and an appropriate message
  - Returns HTTP 200 on success, HTTP 401 on failure
- [ ] Include FastUI router so the frontend is served from `GET /`

---

### Frontend – FastUI

#### `app/ui.py`
- [ ] Define a FastUI page for the login screen rendered at `GET /`
- [ ] Page contains:
  - Heading: "Sign In"
  - `Form` component with:
    - `InputField` for **Username** (type `text`, required)
    - `InputField` for **Password** (type `password`, required)
    - Submit button labelled "Login"
  - The form submits a `POST` request to `/api/login`
- [ ] On success response from the API, display a success message / redirect to a home page
- [ ] On failure response, display an inline error message "Invalid username or password"

---

### API Contract

#### `POST /api/login`

**Request body (JSON):**
```json
{
  "username": "string",
  "password": "string"
}
```

**Success response – HTTP 200:**
```json
{
  "success": true,
  "message": "Login successful"
}
```

**Failure response – HTTP 401:**
```json
{
  "success": false,
  "message": "Invalid username or password"
}
```

---

### Database / Credential Storage
- [ ] For the MVP there is **no database**; credentials are hardcoded strings in `app/auth.py`
- [ ] Document that production usage must replace hardcoded credentials with a proper user store (e.g., PostgreSQL + hashed passwords with bcrypt)

---

### Testing

#### `tests/test_auth.py`
- [ ] Test `authenticate()` returns `True` for correct credentials
- [ ] Test `authenticate()` returns `False` for wrong username
- [ ] Test `authenticate()` returns `False` for wrong password
- [ ] Integration test: `POST /api/login` with valid credentials → HTTP 200 + `success: true`
- [ ] Integration test: `POST /api/login` with invalid credentials → HTTP 401 + `success: false`

---

### Running the Project
- [ ] Document how to run locally:
  ```bash
  # Install dependencies
  uv sync

  # Start the development server
  uv run uvicorn app.main:app --reload
  # Open browser at http://localhost:8000
  ```
- [ ] Document how to run tests:
  ```bash
  uv run pytest
  ```

---

### Future Enhancements (out of scope for MVP)
- Replace hardcoded credentials with a database (e.g., PostgreSQL via SQLAlchemy or SQLModel)
- Add password hashing (bcrypt / argon2)
- Add JWT-based session tokens
- Add logout endpoint
- Add rate limiting / account lockout after N failed attempts
- HTTPS / TLS termination
