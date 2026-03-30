# Agenticworkflow_GHCP — Implementation Plan

## Overview

This plan covers the full-stack implementation of the **agenticworkflow_GHCP** project: a FastAPI
authentication backend, a FastUI frontend, and a **persistent database layer** for storing users,
sessions, and agent-workflow records.

---

## Database Recommendation

### Recommended Database: **PostgreSQL** (production) / **SQLite** (development)

| Criterion | PostgreSQL | SQLite |
|---|---|---|
| ACID compliance | ✅ Full | ✅ Full |
| JSON / JSONB columns | ✅ Native JSONB | ✅ JSON text |
| Concurrent writes | ✅ Excellent | ⚠️ Limited |
| Deployment complexity | Medium (server) | Low (file) |
| Best for | Production workloads | Local dev & tests |

#### Why PostgreSQL?

1. **Relational integrity** — foreign keys between `users`, `sessions`, and `workflow_runs` tables
   guarantee data consistency.
2. **JSONB storage** — agent payloads and workflow state are semi-structured; PostgreSQL's
   native JSONB type allows efficient querying without a separate document store.
3. **Full-text search** — useful for searching agent conversation logs.
4. **Scalability** — connection pooling (via PgBouncer or SQLAlchemy's built-in pool) handles
   concurrent agent runs without bottlenecks.
5. **Ecosystem** — first-class support in SQLAlchemy, Alembic, and all major cloud providers
   (AWS RDS, Azure Database for PostgreSQL, Supabase, Neon).

#### Development shortcut

Use **SQLite** locally (zero setup, file-based) with the **same SQLAlchemy models**. Switch to
PostgreSQL in production by changing the `DATABASE_URL` environment variable — no code changes
required.

---

## Database Schema

### Table: `users`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID (PK) | Generated server-side |
| `username` | VARCHAR(150) UNIQUE NOT NULL | Login identifier |
| `hashed_password` | TEXT NOT NULL | bcrypt hash |
| `is_active` | BOOLEAN DEFAULT TRUE | Soft-disable accounts |
| `created_at` | TIMESTAMPTZ DEFAULT now() | Audit timestamp |

### Table: `sessions`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID (PK) | JWT `jti` claim |
| `user_id` | UUID FK → users.id | Owner of the session |
| `created_at` | TIMESTAMPTZ DEFAULT now() | |
| `expires_at` | TIMESTAMPTZ NOT NULL | Token expiry |
| `revoked` | BOOLEAN DEFAULT FALSE | Logout / token revocation |

### Table: `workflow_runs`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID (PK) | |
| `user_id` | UUID FK → users.id | Who triggered the run |
| `agent_name` | VARCHAR(100) NOT NULL | e.g. `"planningAgent"` |
| `status` | VARCHAR(20) NOT NULL | `pending / running / completed / failed` |
| `input_payload` | JSONB / JSON | Workflow input data |
| `output_payload` | JSONB / JSON | Agent result data |
| `created_at` | TIMESTAMPTZ DEFAULT now() | |
| `updated_at` | TIMESTAMPTZ DEFAULT now() | Updated on status change |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI ≥ 0.110 |
| ORM | SQLAlchemy 2.x (async, `asyncpg` driver) |
| Migrations | Alembic |
| Password hashing | `passlib[bcrypt]` |
| Auth tokens | `python-jose[cryptography]` (JWT) |
| Database (prod) | PostgreSQL ≥ 15 |
| Database (dev) | SQLite (via `aiosqlite`) |
| Frontend | FastUI |
| Package manager | `uv` |

---

## Implementation Task List

### Phase 1 — Database & ORM Setup (Backend)

- [ ] Add dependencies to `backend/pyproject.toml`:
  - `sqlalchemy>=2.0`
  - `alembic>=1.13`
  - `asyncpg>=0.29` (PostgreSQL async driver)
  - `aiosqlite>=0.20` (SQLite async driver for dev)
  - `passlib[bcrypt]>=1.7`
  - `python-jose[cryptography]>=3.3`
- [ ] Create `backend/app/db/` package:
  - `__init__.py`
  - `base.py` — `DeclarativeBase` and shared `metadata`
  - `session.py` — async `engine` + `AsyncSession` factory, reads `DATABASE_URL` from env
- [ ] Create `backend/app/models/` SQLAlchemy models:
  - `user.py` — `User` ORM model mapping to `users` table
  - `session.py` — `Session` ORM model mapping to `sessions` table
  - `workflow_run.py` — `WorkflowRun` ORM model mapping to `workflow_runs` table
- [ ] Initialise Alembic:
  - `alembic init backend/alembic`
  - Configure `alembic/env.py` to use the async engine and import all models
- [ ] Write initial Alembic migration: `alembic revision --autogenerate -m "initial schema"`

### Phase 2 — Authentication Service Rewrite (Backend)

- [ ] Create `backend/app/repositories/user_repository.py`:
  - `get_by_username(db, username) -> User | None`
  - `create_user(db, username, password) -> User`
- [ ] Update `backend/app/services/auth_service.py`:
  - Replace env-var credential check with database lookup + `passlib.verify` call
  - Issue a signed JWT on success (`python-jose`)
  - Return `AuthResponse` with `access_token` and `token_type`
- [ ] Update `backend/app/models/auth.py` Pydantic schemas:
  - `AuthRequest` — `username: str`, `passcode: str`
  - `AuthResponse` — `authenticated: bool`, `message: str`, `access_token: str | None`
- [ ] Add `backend/app/core/security.py`:
  - `hash_password(plain: str) -> str`
  - `verify_password(plain: str, hashed: str) -> bool`
  - `create_access_token(data: dict, expires_delta: timedelta) -> str`
  - `decode_access_token(token: str) -> dict`
- [ ] Update `backend/app/core/config.py`:
  - Add `DATABASE_URL` (default: `sqlite+aiosqlite:///./dev.db`)
  - Add `SECRET_KEY` (read from env, no hardcoded default in production)
  - Add `ACCESS_TOKEN_EXPIRE_MINUTES` (default: `60`)

### Phase 3 — Workflow Run Tracking (Backend)

- [ ] Create `backend/app/repositories/workflow_repository.py`:
  - `create_run(db, user_id, agent_name, input_payload) -> WorkflowRun`
  - `update_run_status(db, run_id, status, output_payload) -> WorkflowRun`
  - `list_runs_for_user(db, user_id) -> list[WorkflowRun]`
- [ ] Create `backend/app/routers/workflows.py`:
  - `POST /workflows/` — start a new workflow run
  - `GET /workflows/` — list runs for authenticated user
  - `GET /workflows/{run_id}` — get a single run's details
- [ ] Register `workflows_router` in `backend/app/main.py`
- [ ] Add JWT bearer dependency (`backend/app/core/dependencies.py`) for protected routes

### Phase 4 — Frontend Updates

- [ ] Update login form to display JWT token on success
- [ ] Add a **Workflow Dashboard** page listing the user's agent runs
- [ ] Update `BACKEND_URL` handling in `frontend/app/main.py`

### Phase 5 — Configuration & Environment

- [ ] Create `backend/.env.example`:
  ```
  DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/agenticworkflow
  VALID_USERNAME=admin
  VALID_PASSCODE=changeme
  SECRET_KEY=replace-with-a-secure-random-string
  ACCESS_TOKEN_EXPIRE_MINUTES=60
  ```
- [ ] Update `backend/README.md` with database setup instructions (PostgreSQL & SQLite)
- [ ] Add `docker-compose.yml` at the repo root for local PostgreSQL:
  ```yaml
  services:
    db:
      image: postgres:16
      environment:
        POSTGRES_DB: agenticworkflow
        POSTGRES_USER: agenticuser
        POSTGRES_PASSWORD: agenticpass
      ports:
        - "5432:5432"
  ```

### Phase 6 — Testing

- [ ] Add `pytest-asyncio` and `httpx` to dev dependencies
- [ ] Write unit tests for `auth_service.py` (mock DB)
- [ ] Write integration tests for `/auth/login` and `/workflows/` endpoints using an in-memory
  SQLite database
- [ ] Ensure all tests pass with `pytest backend/`

---

## Environment Variables Reference

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./dev.db` | SQLAlchemy async connection string |
| `VALID_USERNAME` | `username` | Seed admin username (dev only) |
| `VALID_PASSCODE` | `passcode` | Seed admin passcode (dev only) |
| `SECRET_KEY` | *(must be set)* | JWT signing secret |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | JWT lifetime in minutes |
| `BACKEND_URL` | `http://localhost:8000` | Frontend → backend URL |

---

## Migration Commands (Quick Reference)

```bash
# Apply all pending migrations
cd backend
alembic upgrade head

# Generate a new migration after model changes
alembic revision --autogenerate -m "describe your change"

# Downgrade one step
alembic downgrade -1
```

---

## Local Development Quick Start (with PostgreSQL)

```bash
# 1. Start PostgreSQL
docker compose up -d db

# 2. Set environment variables
export DATABASE_URL="postgresql+asyncpg://agenticuser:agenticpass@localhost:5432/agenticworkflow"
export SECRET_KEY="dev-secret-key-change-in-production"

# 3. Install backend dependencies
cd backend
uv venv && source .venv/bin/activate
uv pip install -e .

# 4. Run database migrations
alembic upgrade head

# 5. Start the API server
uvicorn app.main:app --reload --port 8000
```
