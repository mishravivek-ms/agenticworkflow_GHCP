from __future__ import annotations

import os
from typing import Annotated

import httpx
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastui import AnyComponent, FastUI, prebuilt_html
from fastui import components as c
from fastui.events import GoToEvent
from fastui.forms import fastui_form
from pydantic import BaseModel, Field, SecretStr

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

app = FastAPI(title="Authentication UI")


class LoginForm(BaseModel):
    username: str = Field(title="Username")
    passcode: SecretStr = Field(title="Passcode")


class AuthResponse(BaseModel):
    authenticated: bool
    message: str


@app.get("/api/", response_model=FastUI, response_model_exclude_none=True)
def login_form() -> list[AnyComponent]:
    return [
        c.Page(
            components=[
                c.Heading(text="Sign in", level=2),
                c.Paragraph(text="Enter your credentials to continue."),
                c.ModelForm(
                    model=LoginForm,
                    display_mode="page",
                    submit_url="/api/login",
                ),
            ]
        )
    ]


@app.post("/api/login", response_model=FastUI, response_model_exclude_none=True)
async def login_submit(form: Annotated[LoginForm, fastui_form(LoginForm)]) -> list[AnyComponent]:
    payload = {
        "username": form.username,
        "passcode": form.passcode.get_secret_value(),
    }
    try:
        async with httpx.AsyncClient(base_url=BACKEND_URL, timeout=5.0) as client:
            response = await client.post("/auth/login", json=payload)
            response.raise_for_status()
        auth = AuthResponse.model_validate(response.json())
        status_text = "Authenticated" if auth.authenticated else "Invalid credentials"
        heading = "Login successful" if auth.authenticated else "Login failed"
        message = auth.message
    except httpx.HTTPError:
        heading = "Login error"
        status_text = "Backend unreachable"
        message = "Unable to reach the authentication API."

    return [
        c.Page(
            components=[
                c.Heading(text=heading, level=2),
                c.Paragraph(text=message),
                c.Paragraph(text=status_text),
                c.Link(
                    components=[c.Text(text="Back to sign in")],
                    on_click=GoToEvent(url="/"),
                ),
            ]
        )
    ]


@app.get("/{path:path}")
async def html_landing() -> HTMLResponse:
    return HTMLResponse(prebuilt_html(title="Authentication UI"))
