# Auth Service – Backend

A minimal authentication backend built with **FastAPI** and **FastUI**, managed by **uv**.

## Tech Stack

| Layer       | Technology                                |
|-------------|-------------------------------------------|
| Backend     | FastAPI (Python 3.11+)                    |
| Frontend UI | FastUI (server-driven SPA)               |
| Package Mgr | uv                                        |
| API Style   | REST                                      |
| Data Store  | Hardcoded in-memory (MVP only)           |

---

## Project Layout

```
backend/
├── pyproject.toml
├── README.md
├── app/
│   ├── __init__.py
│   ├── main.py      # FastAPI application entry point
│   ├── auth.py      # Authentication logic
│   ├── models.py    # Pydantic request/response models
│   └── ui.py        # FastUI page definitions
└── tests/
    ├── __init__.py
    └── test_auth.py
```

---

## Setup

```bash
# Install dependencies (from the backend/ directory)
uv sync --extra dev
```

---

## Running the server

```bash
uv run uvicorn app.main:app --reload
# Open http://localhost:8000 in your browser
```

---

## Running tests

```bash
uv run pytest
```

---

## API Reference

### `POST /api/login`

**Request body (JSON):**
```json
{ "username": "string", "password": "string" }
```

**HTTP 200 – success:**
```json
{ "success": true, "message": "Login successful" }
```

**HTTP 401 – failure:**
```json
{ "success": false, "message": "Invalid username or password" }
```

---

## ⚠️ Production Notes

The MVP stores credentials as plain strings in `app/auth.py`.  
Before any production deployment you **must**:

- Replace hardcoded credentials with a proper user store (e.g. PostgreSQL).
- Hash passwords with `bcrypt` or `argon2`.
- Issue JWT session tokens and add a logout endpoint.
- Enable HTTPS / TLS termination.
- Add rate limiting / account lockout after repeated failures.
