# Backend

FastAPI backend that validates credentials against hardcoded values.

## Setup (uv)

```bash
cd backend
uv venv
source .venv/bin/activate
uv pip install -e .
```

## Run

```bash
uvicorn app.main:app --reload
```

## Example API Usage

```bash
curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"username","password":"passcode"}'
```

Expected response:

```json
{"success": true, "message": "Authenticated"}
```
