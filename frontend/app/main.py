from __future__ import annotations

import json
import os

import httpx
from fastapi import FastAPI, Form, Query
from fastapi.responses import HTMLResponse
from fastui import FastUI, prebuilt_html
from fastui.components import FireEvent
from fastui.events import GoToEvent

from app.pages import dashboard_page, login_page

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
DEFAULT_TIMEOUT_SECONDS = 5.0
try:
    BACKEND_TIMEOUT_SECONDS = float(
        os.getenv("BACKEND_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS))
    )
except ValueError:
    BACKEND_TIMEOUT_SECONDS = DEFAULT_TIMEOUT_SECONDS
REQUEST_TIMEOUT = httpx.Timeout(BACKEND_TIMEOUT_SECONDS)

_ERR_UNREACHABLE = "Unable to reach the authentication service."
_ERR_INVALID_RESPONSE = "Authentication service returned an invalid response format."
_ERR_SERVICE_ERROR = "Authentication service returned an error."

app = FastAPI(title="Authentication UI")


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse(prebuilt_html(title="Authentication UI", api_root_url="/api"))


@app.get("/api/", response_model=FastUI)
@app.get("/api", response_model=FastUI)
def api_index(
    error: str | None = Query(default=None),
    success: str | None = Query(default=None),
) -> FastUI:
    """Login page — accepts optional ``error`` and ``success`` query params for banners."""
    return login_page(error=error, success=success)


@app.get("/api/dashboard", response_model=FastUI)
def api_dashboard() -> FastUI:
    """Dashboard page shown after a successful login."""
    return dashboard_page()


@app.post("/api/login", response_model=FastUI)
async def api_login(username: str = Form(...), passcode: str = Form(...)) -> FastUI:
    payload = {"username": username, "passcode": passcode}
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.post(f"{BACKEND_URL}/auth/login", json=payload)
        response.raise_for_status()
        data = response.json()
    except httpx.RequestError:
        return [
            FireEvent(
                event=GoToEvent(url="/", query={"error": _ERR_UNREACHABLE})
            )
        ]
    except httpx.HTTPStatusError as exc:
        try:
            data = exc.response.json()
        except json.JSONDecodeError:
            return [
                FireEvent(
                    event=GoToEvent(
                        url="/",
                        query={"error": _ERR_INVALID_RESPONSE},
                    )
                )
            ]
        message = data.get("message") or _ERR_SERVICE_ERROR
        return [FireEvent(event=GoToEvent(url="/", query={"error": message}))]

    authenticated = bool(data.get("authenticated"))
    if authenticated:
        return [FireEvent(event=GoToEvent(url="/dashboard"))]

    message = data.get("message") or "Invalid credentials."
    return [FireEvent(event=GoToEvent(url="/", query={"error": message}))]
