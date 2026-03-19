# AgenticWorkflow

A full-stack Python application built with **FastAPI** (backend) and **FastUI** (frontend), managed via **uv**.

## Project structure

```
.
├── backend/                  # FastAPI REST API
│   ├── app/
│   │   ├── main.py
│   │   ├── core/             # App configuration
│   │   ├── models/           # Pydantic models
│   │   ├── routers/          # API routers
│   │   └── services/         # Business logic
│   ├── pyproject.toml
│   └── README.md
├── frontend/                 # FastUI web application
│   ├── app/
│   │   └── main.py
│   ├── pyproject.toml
│   └── README.md
└── .github/
    ├── agents/               # GitHub Copilot custom agents
    └── workflows/            # GitHub Actions workflows
```

## Quick start

### 1. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Start the backend

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

### 3. Start the frontend

```bash
cd frontend
uv sync
uv run uvicorn app.main:app --reload --port 8001
```

Open `http://localhost:8001` in your browser.

## Documentation

- [Backend README](backend/README.md)
- [Frontend README](frontend/README.md)