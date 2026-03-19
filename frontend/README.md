# Frontend

## Setup

```bash
cd frontend
uv sync
```

## Run the UI

```bash
BACKEND_URL=http://localhost:8000 uv run uvicorn app.main:app --reload --port 3000
```

Visit `http://localhost:3000` to open the FastUI login form.
