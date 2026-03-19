# agenticworkflow_GHCP

Authentication flow sample with a FastAPI backend and FastUI frontend.

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── models/
│   │   ├── routers/
│   │   ├── services/
│   │   └── main.py
│   ├── pyproject.toml
│   └── README.md
├── frontend/
│   ├── app/
│   │   └── main.py
│   ├── pyproject.toml
│   └── README.md
└── README.md
```

## Quick Start

### Backend

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
uv sync
BACKEND_URL=http://localhost:8000 uv run uvicorn app.main:app --reload --port 3000
```

Open `http://localhost:3000` to see the login UI.
