from fastapi import FastAPI

from app.routers.auth import router as auth_router

app = FastAPI(title="Authentication API")

app.include_router(auth_router, prefix="/auth", tags=["auth"])


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
