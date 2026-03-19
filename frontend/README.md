# Frontend (FastUI)

## Setup

```bash
cd frontend
uv venv
uv sync
```

## Run the UI

```bash
uv run uvicorn app.main:app --reload --port 8001
```

Set the backend URL if it differs from the default:

```bash
export BACKEND_URL="http://localhost:8000"
```

Open http://localhost:8001 in your browser.
