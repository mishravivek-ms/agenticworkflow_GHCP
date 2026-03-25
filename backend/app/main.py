from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.auth import authenticate
from app.models import LoginRequest, LoginResponse
from app.ui import router as ui_router

app = FastAPI(title="Auth Service")

# Mount FastUI router so the login page is served at GET /
app.include_router(ui_router)


@app.post("/api/login", response_model=LoginResponse)
async def login(request: LoginRequest) -> JSONResponse:
    """Authenticate a user and return success or failure."""
    if authenticate(request.username, request.password):
        return JSONResponse(
            status_code=200,
            content=LoginResponse(success=True, message="Login successful").model_dump(),
        )
    return JSONResponse(
        status_code=401,
        content=LoginResponse(
            success=False, message="Invalid username or password"
        ).model_dump(),
    )
