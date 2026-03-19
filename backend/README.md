# Backend (FastAPI)

## Setup

```bash
cd backend
uv venv
uv sync
```

## Run the API

```bash
uv run uvicorn app.main:app --reload
```

## Example Request

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"username","passcode":"passcode"}'
```
