# Authentication Flow — Project Plan

## Overview

Build a minimal **login / authentication** application using :

| Layer    | Technology      |
|----------|-----------------|
| Backend  | FastAPI (Python 3.11+) |
| Frontend | FastUI          |
| Package Manager | uv       |
| API Style | REST           |

The backend validates a username/password pair against hardcoded credentials.  
The frontend provides a login form and displays the result to the user. 

---


## Todo List

### 1. Project Setup

- [ ] Initialise the project directory structure
  ```
  auth-app/
  ├── backend/
  │   ├── main.py
  │   └── pyproject.toml   # managed by uv
  └── frontend/
      ├── main.py
      └── pyproject.toml   # managed by uv
  ```
- [ ] Install **uv** (`pip install uv` or via the official installer)
- [ ] Create backend virtual environment: `uv venv` inside `backend/`
- [ ] Create frontend virtual environment: `uv venv` inside `frontend/`
- [ ] Add backend dependencies to `backend/pyproject.toml`:
  - `fastapi >= 0.110`
  - `uvicorn[standard]`
  - `python-multipart`  (needed for form parsing)
- [ ] Add frontend dependencies to `frontend/pyproject.toml`:
  - `fastui >= 0.6`
  - `fastapi >= 0.110`
  - `uvicorn[standard]`
  - `httpx`            (for async calls to the backend)
- [ ] Install all dependencies: `uv pip install -e .` in each directory

---

### 2. Backend (FastAPI)

#### 2a. Data Models

- [ ] Create a `LoginRequest` Pydantic model with fields:
  - `username: str`
  - `password: str`
- [ ] Create a `LoginResponse` Pydantic model with fields:
  - `success: bool`
  - `message: str`

#### 2b. Hardcoded Credentials

- [ ] Define the expected credentials as module-level constants in `main.py`:
  ```python
  VALID_USERNAME = "username"
  VALID_PASSWORD = "passcode"
  ```

#### 2c. REST Endpoint

- [ ] Create `POST /api/login` endpoint that:
  1. Accepts a JSON body matching `LoginRequest`
  2. Compares `username` and `password` against the hardcoded values
  3. Returns `LoginResponse(success=True, message="Login successful")` on match
  4. Returns `LoginResponse(success=False, message="Invalid credentials")` (HTTP 401) on mismatch

#### 2d. CORS

- [ ] Add `CORSMiddleware` to allow the frontend origin (e.g. `http://localhost:3000`) so the browser can call the backend API

#### 2e. Run the Backend 

- [ ] Start with: `uvicorn main:app --reload --port 8000`

---

### 3. Frontend (FastUI)

#### 3a. FastUI Page Structure

- [ ] Create a root FastAPI app that serves the FastUI SPA shell at `GET /`
- [ ] Mount FastUI's static assets (JS/CSS) using `fastui.serve_static_app`

#### 3b. Login Form Page

- [ ] Create `GET /api/ui/login` route that returns a FastUI `Page` containing:
  - A `Heading` component: **"Sign In"**
  - A `Form` component with:
    - `username` — `InputField` (type `text`, required)
    - `password` — `InputField` (type `password`, required)
    - Submit button label: **"Login"**
  - The form `submit_url` should point to the backend: `http://localhost:8000/api/login`

#### 3c. Result Page / Feedback

- [ ] After the form is submitted via FastUI, display a result `Page`:
  - On success: show a green `Text` component with **"Welcome! You are logged in."**
  - On failure: show a red `Text` component with **"Invalid username or password. Please try again."** and a link back to the login page

#### 3d. Run the Frontend

- [ ] Start with: `uvicorn main:app --reload --port 3000`

---

### 4. Database Layer

> **Note:** For this initial version, no database is required — credentials are hardcoded in the backend.  
> The section below describes what to add if/when you extend to a real database.

- [ ] *(Future)* Add SQLite (or PostgreSQL) via **SQLModel** or **SQLAlchemy**
- [ ] *(Future)* Create a `users` table: `id`, `username`, `hashed_password`, `created_at`
- [ ] *(Future)* Hash passwords with **bcrypt** (`passlib[bcrypt]`) before storing
- [ ] *(Future)* Replace hardcoded credential check with a DB query + bcrypt verify

---

### 5. API Contract

| Method | Path            | Request Body                        | Response Body                                |
|--------|-----------------|-------------------------------------|----------------------------------------------|
| POST   | `/api/login`    | `{"username": "...", "password": "..."}` | `{"success": true/false, "message": "..."}` |
| GET    | `/api/ui/login` | —                                   | FastUI `Page` JSON (login form)              |
| GET    | `/`             | —                                   | FastUI SPA shell (HTML)                      |

---

### 6. Testing

- [ ] Write a `pytest` test for the `/api/login` endpoint using FastAPI's `TestClient`:
  - Test case: correct credentials → HTTP 200, `success=true`
  - Test case: wrong password → HTTP 401, `success=false`
  - Test case: wrong username → HTTP 401, `success=false`
  - Test case: missing fields → HTTP 422 (validation error)

---

### 7. Developer Experience

- [ ] Add a `Makefile` (or `justfile`) with shortcuts:
  - `make backend` — start backend on port 8000
  - `make frontend` — start frontend on port 3000
  - `make test` — run pytest
- [ ] Add a root-level `README.md` explaining:
  - Prerequisites (Python 3.11+, uv)
  - How to install dependencies
  - How to run backend and frontend
  - Default credentials for testing (`username` / `passcode`)

---

### 8. Delivery Checklist

- [ ] Project directory structure created
- [ ] `uv` used for all dependency management
- [ ] Backend FastAPI app runs without errors
- [ ] Frontend FastUI app renders login form in the browser
- [ ] Correct credentials → success message displayed
- [ ] Incorrect credentials → error message displayed
- [ ] All `pytest` tests pass
- [ ] README updated with run instructions
