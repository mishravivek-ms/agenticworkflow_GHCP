# agenticworkflow_GHCP

Authentication flow scaffold with a FastAPI backend and FastUI frontend.

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/
│   │   ├── models/
│   │   ├── services/
│   │   └── core/
│   ├── pyproject.toml
│   └── README.md
├── frontend/
│   ├── app/
│   ├── pyproject.toml
│   └── README.md
└── README.md
```

## Quick Start

Start the backend in one terminal:

```bash
cd backend
uv venv
source .venv/bin/activate
uv pip install -e .
uvicorn app.main:app --reload --port 8000
```

Start the frontend in another terminal:

```bash
cd frontend
uv venv
source .venv/bin/activate
uv pip install -e .
export BACKEND_URL="http://localhost:8000"
uvicorn app.main:app --reload --port 8001
```

Visit `http://localhost:8001` to use the login UI.
