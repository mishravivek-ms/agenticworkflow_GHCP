# Frontend — FastUI

Browser UI built with **FastUI** and served by **FastAPI**, managed via **uv**.

## Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) installed
- The backend server running on `http://localhost:8000`

## Setup

```bash
# From the frontend/ directory
uv sync
```

## Running the server

```bash
uv run uvicorn app.main:app --reload --port 8001
```

Open `http://localhost:8001` in your browser.

## Project structure

```
frontend/
├── app/
│   └── main.py   # FastUI pages and API proxy calls
└── pyproject.toml
```

## Pages

| Route     | Description            |
|-----------|------------------------|
| `/`       | Home / landing page    |
| `/items/` | Item list (from API)   |
