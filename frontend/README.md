# Frontend (FastUI)

## Setup

```bash
cd frontend
uv venv
source .venv/bin/activate
uv pip install -e .
```

## Run

```bash
export BACKEND_URL="http://localhost:8000"
uvicorn app.main:app --reload --port 8001
```

## Notes

- The login form submits to the frontend API, which calls the backend `/auth/login` endpoint.
