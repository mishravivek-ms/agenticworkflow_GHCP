"""
FastUI frontend for the authentication app.

Routes:
  GET  /                     — FastUI SPA shell (HTML)
  GET  /api/ui/login         — Login form page
  POST /api/login/submit     — Proxy: call backend, redirect to result page
  GET  /api/ui/success       — Success result page
  GET  /api/ui/failure       — Failure result page
"""

from typing import Annotated

import httpx
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastui import AnyComponent, FastUI, prebuilt_html
from fastui import components as c
from fastui.events import GoToEvent, PageEvent
from fastui.forms import fastui_form
from pydantic import BaseModel, Field, SecretStr

app = FastAPI(title="Auth App Frontend")

BACKEND_LOGIN_URL = "http://localhost:8000/api/login"


# ---------------------------------------------------------------------------
# Pydantic model for the login form
# ---------------------------------------------------------------------------

class LoginForm(BaseModel):
    """Fields rendered by FastUI as a login form."""

    username: str = Field(title="Username")
    password: SecretStr = Field(title="Password")


# ---------------------------------------------------------------------------
# SPA shell — serves the React/FastUI single-page application
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    """Return the FastUI SPA HTML shell."""
    return HTMLResponse(prebuilt_html(title="Login App"))


# ---------------------------------------------------------------------------
# Login form page
# ---------------------------------------------------------------------------

@app.get("/api/ui/login", response_model=FastUI, response_model_exclude_none=True)
async def login_page() -> list[AnyComponent]:
    """Render the Sign In page with a username/password form."""
    return [
        c.Page(
            components=[
                c.Heading(text="Sign In", level=1),
                c.ModelForm(
                    model=LoginForm,
                    submit_url="/api/login/submit",
                    submit_trigger=PageEvent(name="submit"),
                ),
            ]
        )
    ]


# ---------------------------------------------------------------------------
# Form submission proxy — forwards credentials to the backend
# ---------------------------------------------------------------------------

@app.post("/api/login/submit", response_model=FastUI, response_model_exclude_none=True)
async def login_submit(
    form: Annotated[LoginForm, fastui_form(LoginForm)],
) -> list[AnyComponent]:
    """
    Receive the FastUI form submission, call the backend /api/login,
    then redirect to the appropriate result page.
    """
    success = False
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                BACKEND_LOGIN_URL,
                json={
                    "username": form.username,
                    "password": form.password.get_secret_value(),
                },
                timeout=5.0,
            )
        # Accept only 2xx responses as potentially successful; treat anything
        # else (4xx / 5xx) as a failed login without exposing internal errors.
        if response.is_success or response.status_code == 401:
            data = response.json()
            success = bool(data.get("success", False))
    except httpx.RequestError as exc:
        # Log connection / timeout errors so operators can diagnose issues
        # without leaking details to the end user.
        import logging
        logging.getLogger(__name__).warning("Backend request failed: %s", exc)

    target = "/api/ui/success" if success else "/api/ui/failure"
    return [c.FireEvent(event=GoToEvent(url=target))]


# ---------------------------------------------------------------------------
# Result pages
# ---------------------------------------------------------------------------

@app.get("/api/ui/success", response_model=FastUI, response_model_exclude_none=True)
async def success_page() -> list[AnyComponent]:
    """Display a success message after a valid login."""
    return [
        c.Page(
            components=[
                c.Heading(text="Login Successful", level=1),
                c.Paragraph(
                    text="Welcome! You are logged in.",
                    class_name="text-success fw-semibold",
                ),
            ]
        )
    ]


@app.get("/api/ui/failure", response_model=FastUI, response_model_exclude_none=True)
async def failure_page() -> list[AnyComponent]:
    """Display an error message and a link back to the login page."""
    return [
        c.Page(
            components=[
                c.Heading(text="Login Failed", level=1),
                c.Paragraph(
                    text="Invalid username or password. Please try again.",
                    class_name="text-danger fw-semibold",
                ),
                c.Link(
                    components=[c.Text(text="Back to Login")],
                    on_click=GoToEvent(url="/api/ui/login"),
                ),
            ]
        )
    ]
