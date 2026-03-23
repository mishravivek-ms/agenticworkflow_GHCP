import logging

from fastapi import FastAPI

from app.core.config import settings
from app.routers.auth import router as auth_router

logger = logging.getLogger(__name__)

app = FastAPI(title="Authentication Service")
app.include_router(auth_router, prefix="/api")

if settings.auth_username == "username" and settings.auth_password == "passcode":
    logger.warning("Using default credentials for development; set AUTH_USERNAME/AUTH_PASSWORD for production.")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
