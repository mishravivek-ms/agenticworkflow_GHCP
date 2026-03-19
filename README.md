# agenticworkflow_GHCP

Authentication flow sample with a FastAPI backend and FastUI frontend.

## Project Structure

```
.
├── backend/
│   ├── app/
│   ├── pyproject.toml
│   └── README.md
├── frontend/
│   ├── app/
│   ├── pyproject.toml
│   └── README.md
└── README.md
```

## Quick Start

1. Start the backend:
   ```bash
   cd backend
   uv venv
   uv sync
   uv run uvicorn app.main:app --reload
   ```
2. Start the frontend in another terminal:
   ```bash
   cd frontend
   uv venv
   uv sync
   uv run uvicorn app.main:app --reload --port 8001
   ```
3. Visit http://localhost:8001 and sign in with:
   - Username: `username`
   - Passcode: `passcode`
