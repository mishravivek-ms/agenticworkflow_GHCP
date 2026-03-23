# Frontend

FastUI-based frontend that submits credentials to the backend API.

## Setup (uv)

```bash
cd frontend
uv venv
source .venv/bin/activate
uv pip install -e .
```

## Run

```bash
uvicorn app.main:app --reload --port 8001
```

The frontend expects the backend at `http://localhost:8000`. Update `frontend/app/core/config.py` if you need a different backend URL.
