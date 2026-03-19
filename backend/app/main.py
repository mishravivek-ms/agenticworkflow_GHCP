from fastapi import FastAPI

from app.routers import auth

app = FastAPI(title="Authentication API")

app.include_router(auth.router, prefix="/auth", tags=["auth"])


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
