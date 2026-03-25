from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from app.auth import authenticate
from app.models import LoginRequest, LoginResponse

app = FastAPI(title="Auth Backend")

# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------

@app.post("/api/login")
async def login(request: LoginRequest) -> Response:
    """Authenticate a user and return an appropriate HTTP response.

    Returns HTTP 200 with ``success: true`` on valid credentials, or
    HTTP 401 with ``success: false`` on invalid credentials.
    """
    if authenticate(request.username, request.password):
        body = LoginResponse(success=True, message="Login successful")
        return JSONResponse(content=body.model_dump(), status_code=200)

    body = LoginResponse(success=False, message="Invalid username or password")
    return JSONResponse(content=body.model_dump(), status_code=401)


# ---------------------------------------------------------------------------
# Serve the static frontend
# ---------------------------------------------------------------------------
# Resolve the path to the sibling "frontend" directory so the app can be
# started from any working directory.
_FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

if _FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(_FRONTEND_DIR), html=True), name="frontend")
