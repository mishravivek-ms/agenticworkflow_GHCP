# agenticworkflow_GHCP

## Auth App – Basic Authentication Flow

A full-stack application with a login UI and a REST API backend that authenticates a user against hardcoded credentials.

**Tech Stack**
- Backend: FastAPI (Python 3.11+)
- Frontend: FastUI
- Package Manager: uv
- API Style: REST

## Running the Application

> **Note:** The backend (`backend/main.py`, `backend/auth.py`, `backend/models.py`) must be implemented before the application can start. The frontend UI defined in `frontend/ui.py` is served by the FastAPI backend.

```bash
uv run uvicorn backend.main:app --reload
```

- Application: <http://localhost:8000/>
- Login UI (FastUI): <http://localhost:8000/>
- API docs (Swagger UI): <http://localhost:8000/docs>