# agenticworkflow_GHCP

Authentication flow example with a FastAPI backend and FastUI frontend.

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
│   │   ├── main.py
│   │   ├── models/
│   │   ├── services/
│   │   └── core/
│   ├── pyproject.toml
│   └── README.md
└── README.md
```

## Quickstart (uv)

### Backend

```bash
cd backend
uv venv
source .venv/bin/activate
uv pip install -e .
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
uv venv
source .venv/bin/activate
uv pip install -e .
uvicorn app.main:app --reload --port 8001
```

Open `http://localhost:8001` to use the login screen. The frontend calls the backend at `http://localhost:8000`.
