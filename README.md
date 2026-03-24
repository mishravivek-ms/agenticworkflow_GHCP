# agenticworkflow_GHCP

A minimal **login / authentication** application built with FastAPI (backend) and FastUI (frontend).

---

## Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager (`pip install uv`)

---

## Project Structure

```
auth-app/
├── backend/
│   ├── main.py
│   └── pyproject.toml
└── frontend/
    ├── main.py
    └── pyproject.toml
```

---

## Installation

Install dependencies for each service using `uv`:

```bash
# Backend
cd backend && uv pip install -e .

# Frontend
cd frontend && uv pip install -e .
```

Or use the Makefile shortcut:

```bash
make install
```

---

## Running the Application

### Start the backend (port 8000)

```bash
make backend
# or: cd backend && uvicorn main:app --reload --port 8000
```

### Start the frontend (port 3000)

```bash
make frontend
# or: cd frontend && uvicorn main:app --reload --port 3000
```

Open your browser at **http://localhost:3000** to see the login form.

---

## Default Credentials (for testing)

| Field    | Value      |
|----------|------------|
| Username | `username` |
| Password | `passcode` |

---

## Running Tests

```bash
make test
# or: cd backend && python -m pytest tests/ -v
```

---

## API Contract

| Method | Path            | Description                        |
|--------|-----------------|------------------------------------|
| POST   | `/api/login`    | Authenticate with username/password |
| GET    | `/api/ui/login` | FastUI login form page             |
| GET    | `/`             | FastUI SPA shell                   |