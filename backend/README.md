# Backend

## Setup

```bash
cd backend
uv sync
```

## Run the API

```bash
uv run uvicorn app.main:app --reload --port 8000
```

The API defaults to `username` / `passcode`. Override them with:

```bash
EXPECTED_USERNAME=yourname EXPECTED_PASSCODE=yourpass uv run uvicorn app.main:app --reload --port 8000
```

## Example API Usage

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "username", "passcode": "passcode"}'
```

A successful response returns:

```json
{
  "authenticated": true,
  "message": "Authenticated successfully."
}
```
