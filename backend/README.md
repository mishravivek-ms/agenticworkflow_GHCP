# Backend (FastAPI)

## Setup

```bash
cd backend
uv venv
source .venv/bin/activate
uv pip install -e .
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

## Configuration

Set `VALID_USERNAME` and `VALID_PASSCODE` environment variables to override the
default development credentials.

## Example API Usage

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"username","passcode":"passcode"}'
```
