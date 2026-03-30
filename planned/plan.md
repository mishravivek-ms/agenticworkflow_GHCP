# Login Functionality Implementation Plan

## Overview

This plan covers the full implementation of a robust Login functionality for the `agenticworkflow_GHCP` project. The existing codebase is an authentication scaffold with a **FastAPI** backend and **FastUI** frontend. Credentials are currently validated against environment variables with no persistent storage. This plan extends the scaffold into a production-quality login system with a user database, JWT session tokens, enhanced security controls, and an improved UI.

---

## Current State

| Layer | Status |
|-------|--------|
| Backend | `POST /auth/login` validates username + passcode against env vars |
| Frontend | FastUI form POSTs to `/api/login`, calls backend, shows result page |
| Database | **None** – credentials live in `VALID_USERNAME` / `VALID_PASSCODE` env vars |
| Session management | **None** – stateless, no token issued on success |
| Security | Constant-time compare only – no rate limiting, lockout, or hashing |

---

## Goals

- [ ] Persist users in a database with hashed passwords
- [ ] Issue JWT access tokens on successful login
- [ ] Protect sensitive routes with token-based authentication middleware
- [ ] Implement security hardening: rate limiting, account lockout, password policy
- [ ] Improve the frontend login UI (error display, loading state, redirect on success)
- [ ] Write unit and integration tests for every new layer
- [ ] Provide clear setup and migration instructions

---

## Tech Stack (Additions)

| Concern | Library / Tool |
|---------|---------------|
| Database ORM | SQLAlchemy 2.x (async) |
| Database driver | `aiosqlite` (dev/test) / `asyncpg` for PostgreSQL (production) |
| Migrations | Alembic |
| Password hashing | `passlib[bcrypt]` |
| JWT tokens | `python-jose[cryptography]` |
| Rate limiting | `slowapi` (Starlette middleware) |
| Settings management | `pydantic-settings` |
| Testing | `pytest`, `pytest-asyncio`, `httpx` (async test client) |

---

## Directory Structure (After Implementation)

```
backend/
├── app/
│   ├── main.py                    # FastAPI app factory
│   ├── core/
│   │   ├── config.py              # Pydantic-settings based configuration
│   │   ├── security.py            # Password hashing & JWT helpers
│   │   └── database.py            # Async SQLAlchemy engine & session factory
│   ├── models/
│   │   ├── auth.py                # Pydantic request/response schemas
│   │   └── user.py                # SQLAlchemy ORM User model
│   ├── routers/
│   │   └── auth.py                # /auth/login, /auth/me, /auth/logout
│   ├── services/
│   │   └── auth_service.py        # Business logic (authenticate, create_user)
│   └── middleware/
│       └── rate_limit.py          # Rate limiting middleware
├── alembic/                       # Database migration scripts
│   ├── env.py
│   └── versions/
│       └── 001_create_users_table.py
├── tests/
│   ├── conftest.py                # Test fixtures (in-memory DB, async client)
│   ├── test_auth_router.py        # Router-level integration tests
│   ├── test_auth_service.py       # Unit tests for auth service
│   └── test_security.py           # Unit tests for hashing & JWT
└── pyproject.toml

frontend/
├── app/
│   ├── main.py                    # FastAPI + FastUI app
│   ├── pages/
│   │   ├── login.py               # Login form page builder
│   │   └── dashboard.py           # Post-login dashboard page
│   └── utils/
│       └── auth_client.py         # httpx calls to backend
└── pyproject.toml
```

---

## Implementation Tasks

### 1. Backend – Configuration (`backend/app/core/config.py`)

- [ ] Replace raw `os.getenv` calls with a `pydantic-settings` `BaseSettings` class named `Settings`
- [ ] Add the following settings:
  - `DATABASE_URL: str` – SQLAlchemy async URL (default: `sqlite+aiosqlite:///./auth.db`)
  - `SECRET_KEY: str` – signing key for JWTs (must be set; no insecure default in production)
  - `ACCESS_TOKEN_EXPIRE_MINUTES: int` – token TTL (default: `30`)
  - `ALGORITHM: str` – JWT algorithm (default: `"HS256"`)
  - `MAX_LOGIN_ATTEMPTS: int` – lockout threshold (default: `5`)
  - `LOCKOUT_DURATION_SECONDS: int` – lockout window (default: `300`)
  - `RATE_LIMIT: str` – requests per window for rate limiting (default: `"10/minute"`)
- [ ] Export a single `settings` singleton used across the app

---

### 2. Backend – Database Setup (`backend/app/core/database.py`)

- [ ] Create an async SQLAlchemy engine using `settings.DATABASE_URL`
- [ ] Define an `AsyncSessionLocal` session factory
- [ ] Provide a `get_db` FastAPI dependency that yields an async session and handles commit/rollback/close
- [ ] Provide a `create_all_tables()` coroutine called during app startup

---

### 3. Backend – ORM User Model (`backend/app/models/user.py`)

Define a `User` SQLAlchemy table with the following columns:

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `Integer` | Primary key, auto-increment |
| `username` | `String(64)` | Unique, not null, indexed |
| `hashed_password` | `String(128)` | Not null |
| `is_active` | `Boolean` | Default `True` |
| `failed_login_attempts` | `Integer` | Default `0` |
| `locked_until` | `DateTime` | Nullable |
| `created_at` | `DateTime` | Default `utcnow` |
| `last_login_at` | `DateTime` | Nullable |

---

### 4. Backend – Pydantic Schemas (`backend/app/models/auth.py`)

Update / add the following schemas:

- [ ] `LoginRequest` – `username: str`, `password: str` (rename `passcode` → `password`)
- [ ] `LoginResponse` – `authenticated: bool`, `message: str`, `access_token: str | None`, `token_type: str = "bearer"`
- [ ] `TokenPayload` – `sub: str`, `exp: datetime`
- [ ] `UserCreate` – `username: str`, `password: str` (used for seeding / registration)
- [ ] `UserRead` – `id: int`, `username: str`, `is_active: bool`, `created_at: datetime`

---

### 5. Backend – Security Helpers (`backend/app/core/security.py`)

- [ ] `hash_password(plain: str) -> str` – bcrypt hash using `passlib`
- [ ] `verify_password(plain: str, hashed: str) -> bool` – constant-time bcrypt verify
- [ ] `create_access_token(data: dict, expires_delta: timedelta | None = None) -> str` – sign JWT with `SECRET_KEY` and `ALGORITHM`
- [ ] `decode_access_token(token: str) -> TokenPayload | None` – decode and validate JWT; return `None` on failure
- [ ] `get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User` – FastAPI dependency for protected routes

---

### 6. Backend – Auth Service (`backend/app/services/auth_service.py`)

Replace environment-variable comparison with database-backed logic:

- [ ] `get_user_by_username(db, username) -> User | None`
- [ ] `authenticate_user(db, username, password) -> User | None`:
  - Fetch user from DB
  - Check `locked_until` – raise `HTTP 423 Locked` if account is still locked
  - Call `verify_password`
  - On failure: increment `failed_login_attempts`; lock account if threshold exceeded; persist changes
  - On success: reset `failed_login_attempts` to `0`; update `last_login_at`; persist changes
  - Return `User` on success, `None` on failure
- [ ] `create_user(db, user_create: UserCreate) -> User` – hash password, insert row, return ORM object

---

### 7. Backend – Auth Router (`backend/app/routers/auth.py`)

Update endpoints:

- [ ] **`POST /auth/login`**
  - Accept `LoginRequest` JSON body
  - Call `authenticate_user`; on `None`, return `HTTP 401`
  - Call `create_access_token`; return `LoginResponse` with token
  - Apply rate-limiting decorator (see §9)
- [ ] **`GET /auth/me`** *(new)*
  - Depends on `get_current_user`
  - Returns `UserRead` of the authenticated caller
- [ ] **`POST /auth/logout`** *(new – optional/client-side)*
  - Stateless JWT approach: instruct client to discard token
  - Returns `{"message": "Logged out successfully"}`

---

### 8. Backend – Database Migrations (Alembic)

- [ ] Initialise Alembic inside `backend/`: `alembic init alembic`
- [ ] Configure `alembic/env.py` to import `Base.metadata` from `app.models.user` and use `settings.DATABASE_URL`
- [ ] Generate first migration: `alembic revision --autogenerate -m "create users table"`
- [ ] Document migration commands in `backend/README.md`

---

### 9. Backend – Rate Limiting (`backend/app/middleware/rate_limit.py`)

- [ ] Add `slowapi` dependency to `backend/pyproject.toml`
- [ ] Create a `Limiter` instance keyed by client IP
- [ ] Apply `@limiter.limit(settings.RATE_LIMIT)` to `POST /auth/login`
- [ ] Add `SlowAPIMiddleware` to the FastAPI app in `main.py`

---

### 10. Backend – App Factory Updates (`backend/app/main.py`)

- [ ] Add startup event to call `create_all_tables()`
- [ ] Register `SlowAPIMiddleware`
- [ ] Optionally seed a default admin user if the DB is empty (dev mode only)

---

### 11. Frontend – Login Page UI (`frontend/app/pages/login.py`)

- [ ] Extract login page builder into its own module `frontend/app/pages/login.py`
- [ ] Add inline error display (red text) when the backend returns `401` or network error
- [ ] Show a loading/spinner state while the HTTP call is in flight (FastUI `c.Spinner` or disabled button)
- [ ] Rename the `passcode` field label to `Password`
- [ ] On successful login, store the returned `access_token` in a cookie or `localStorage` via a FastUI `GoToEvent` redirect to `/dashboard`

---

### 12. Frontend – Dashboard Page (`frontend/app/pages/dashboard.py`)

- [ ] Add a `/dashboard` page that shows the logged-in username (fetched from backend `GET /auth/me`)
- [ ] If no valid token is found in the request cookie/header, redirect to `/`
- [ ] Display a "Sign out" button that clears the token and redirects to `/`

---

### 13. Frontend – Auth HTTP Client (`frontend/app/utils/auth_client.py`)

- [ ] Extract all `httpx` calls from `main.py` into a dedicated `auth_client.py` module
- [ ] `login(username, password) -> LoginResponse`
- [ ] `get_me(token: str) -> UserRead`
- [ ] Handle connection errors, timeouts, and unexpected status codes uniformly
- [ ] Configure `BACKEND_URL` and `BACKEND_TIMEOUT_SECONDS` from environment via `pydantic-settings`

---

### 14. Frontend – App Router Updates (`frontend/app/main.py`)

- [ ] Register new routes: `GET /`, `GET /api`, `POST /api/login`, `GET /dashboard`, `POST /api/logout`
- [ ] Add middleware/dependency to validate token cookie on protected routes

---

### 15. Dependency Updates (`pyproject.toml`)

**Backend additions:**
```
sqlalchemy[asyncio]>=2.0.0
aiosqlite>=0.20.0
alembic>=1.13.0
passlib[bcrypt]>=1.7.4
python-jose[cryptography]>=3.3.0
pydantic-settings>=2.2.0
slowapi>=0.1.9
```

**Frontend additions:**
```
pydantic-settings>=2.2.0
```

---

### 16. Testing

#### Unit Tests (`backend/tests/`)

- [ ] **`test_security.py`**
  - `hash_password` returns bcrypt hash
  - `verify_password` returns `True` for correct password, `False` for wrong
  - `create_access_token` returns a decodable JWT with correct `sub` and `exp`
  - `decode_access_token` returns `None` for expired/invalid tokens

- [ ] **`test_auth_service.py`**
  - `authenticate_user` returns `User` for valid credentials
  - Returns `None` for wrong password
  - Returns `None` for non-existent user
  - Increments `failed_login_attempts` on failure
  - Locks account after `MAX_LOGIN_ATTEMPTS` failures
  - Resets counter on successful login

- [ ] **`test_auth_router.py`** (integration, async `httpx` client)
  - `POST /auth/login` with correct credentials → `200` + token
  - `POST /auth/login` with wrong credentials → `401`
  - `POST /auth/login` with missing fields → `422`
  - `GET /auth/me` with valid token → `200` + user info
  - `GET /auth/me` without token → `401`
  - `GET /auth/me` with expired token → `401`
  - Rate limit: 11th request within 1 minute → `429`

#### Test Fixtures (`backend/tests/conftest.py`)

- [ ] In-memory SQLite database via `sqlite+aiosqlite:///:memory:`
- [ ] Override `get_db` dependency with test session
- [ ] Create tables and seed a test user before each test
- [ ] Async `httpx.AsyncClient` pointing at the test app

---

### 17. Environment Variables Reference

Update `backend/README.md` and root `README.md` with:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | No | `sqlite+aiosqlite:///./auth.db` | SQLAlchemy async connection string |
| `SECRET_KEY` | **Yes (prod)** | *(generated warning)* | JWT signing key (min 32 chars) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` | JWT lifetime in minutes |
| `ALGORITHM` | No | `HS256` | JWT signing algorithm |
| `MAX_LOGIN_ATTEMPTS` | No | `5` | Failed attempts before lockout |
| `LOCKOUT_DURATION_SECONDS` | No | `300` | Lockout window in seconds |
| `RATE_LIMIT` | No | `10/minute` | Rate limit for `/auth/login` |
| `BACKEND_URL` | No | `http://localhost:8000` | Frontend → backend URL |
| `BACKEND_TIMEOUT_SECONDS` | No | `5.0` | HTTP client timeout (seconds) |

---

### 18. Security Checklist

- [ ] Passwords stored as bcrypt hashes (never plaintext)
- [ ] JWT signed with `HS256` (rotate `SECRET_KEY` to invalidate all tokens)
- [ ] Constant-time password comparison via bcrypt (prevents timing attacks)
- [ ] Account lockout after configurable failed attempts
- [ ] Rate limiting on login endpoint (prevents brute force)
- [ ] `SECRET_KEY` must be provided via environment variable in production; app warns if missing or too short
- [ ] HTTPS enforced in production (document in README; add `Strict-Transport-Security` header)
- [ ] Tokens transmitted in `Authorization: Bearer <token>` header or `HttpOnly` cookie
- [ ] No sensitive data logged (passwords, tokens)

---

### 19. Documentation Updates

- [ ] Update `backend/README.md`: new env vars, Alembic migration commands, API endpoints
- [ ] Update `frontend/README.md`: new routes, token cookie behaviour, dashboard
- [ ] Update root `README.md`: architecture diagram, end-to-end login flow description

---

## End-to-End Login Flow (After Implementation)

```
User (browser)
  │
  │  GET /               (frontend FastUI app)
  │◄──────────────────── HTML login page rendered
  │
  │  POST /api/login     username + password form submit
  │─────────────────────►
  │                       Frontend calls POST http://backend:8000/auth/login
  │                         ├─ Rate limiter checks IP
  │                         ├─ Fetch User from DB by username
  │                         ├─ Verify bcrypt(password, hashed_password)
  │                         ├─ Check account lockout
  │                         ├─ Update failed_attempts / last_login_at
  │                         └─ Issue JWT access_token
  │◄──────────────────── { authenticated: true, access_token: "eyJ..." }
  │
  │  Redirect to /dashboard (token stored in cookie/localStorage)
  │
  │  GET /dashboard      with Authorization: Bearer <token>
  │─────────────────────►
  │                       Frontend calls GET http://backend:8000/auth/me
  │                         ├─ Decode & validate JWT
  │                         └─ Return UserRead
  │◄──────────────────── Dashboard page with username displayed
```

---

## Acceptance Criteria

1. A user record stored in the database can log in through the UI.
2. A valid JWT is returned on successful login.
3. The `/auth/me` endpoint returns the user's profile when called with a valid token.
4. Failed login attempts increment a counter; after 5 failures the account is locked for 5 minutes.
5. The login endpoint returns HTTP 429 after 10 requests per minute from the same IP.
6. All passwords are stored as bcrypt hashes; no plaintext credentials in the DB or logs.
7. All unit and integration tests pass (`pytest backend/tests/`).
8. The frontend redirects to the dashboard on success and shows an error message on failure.
