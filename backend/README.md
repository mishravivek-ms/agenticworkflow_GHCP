# Auth Backend

A minimal FastAPI backend providing a login API for the authentication flow.

## Tech Stack

| Layer       | Technology              |
|-------------|-------------------------|
| Backend     | FastAPI (Python 3.11+)  |
| Package Mgr | uv                      |
| API Style   | REST                    |
| Data Store  | Hardcoded in-memory (MVP only) |

## Project Layout

```
backend/
├── pyproject.toml
├── README.md
├── app/
│   ├── __init__.py
│   ├── main.py       # FastAPI application entry point
│   ├── auth.py       # Authentication logic
│   └── models.py     # Pydantic request/response models
└── tests/
    ├── __init__.py
    └── test_auth.py
```

## Running Locally

```bash
# Install dependencies (run from the backend/ directory)
uv sync

# Start the development server
uv run uvicorn app.main:app --reload

# Open browser at http://localhost:8000
```

## Running Tests

```bash
uv run pytest
```

## API Contract

### `POST /api/login`

**Request body (JSON):**
```json
{ "username": "string", "password": "string" }
```

**Success – HTTP 200:**
```json
{ "success": true, "message": "Login successful" }
```

**Failure – HTTP 401:**
```json
{ "success": false, "message": "Invalid username or password" }
```

## Production Notes

> ⚠️ The MVP uses hardcoded credentials in `app/auth.py`.  
> Production deployments **must** replace these with a proper user store  
> (e.g., PostgreSQL + bcrypt-hashed passwords).
