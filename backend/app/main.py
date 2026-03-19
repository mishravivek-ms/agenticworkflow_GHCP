from fastapi import FastAPI

from app.routers import auth_router

app = FastAPI(title="Authentication API")

app.include_router(auth_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
