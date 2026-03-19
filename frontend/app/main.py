from __future__ import annotations

import os

import httpx
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastui import FastUI, components as c, prebuilt_html
from fastui.events import GoToEvent

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
BACKEND_TIMEOUT = 5.0

app = FastAPI(title="Authentication UI")


def login_page(message: str | None = None) -> FastUI:
    components = [c.Heading(text="Sign in", level=2)]
    if message:
        components.append(c.Text(text=message))
    components.append(
        c.Form(
            submit_url="/api/login",
            form_fields=[
                c.FormField(name="username", title="Username", required=True),
                c.FormField(
                    name="passcode",
                    title="Passcode",
                    required=True,
                    input_type="password",
                ),
            ],
            footer=[c.Button(text="Sign in", type="submit")],
        )
    )
    return [c.Page(components=components)]


def result_page(message: str, authenticated: bool) -> FastUI:
    status = "Success" if authenticated else "Failed"
    return [
        c.Page(
            components=[
                c.Heading(text=f"Login {status}", level=2),
                c.Text(text=message),
                c.Button(text="Back to form", on_click=GoToEvent(url="/")),
            ]
        )
    ]


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse(prebuilt_html(title="Authentication UI", api_root_url="/api"))


@app.get("/api", response_model=FastUI)
def api_index() -> FastUI:
    return login_page()


@app.post("/api/login", response_model=FastUI)
async def api_login(username: str = Form(...), passcode: str = Form(...)) -> FastUI:
    payload = {"username": username, "passcode": passcode}
    try:
        async with httpx.AsyncClient(timeout=BACKEND_TIMEOUT) as client:
            response = await client.post(f"{BACKEND_URL}/auth/login", json=payload)
        response.raise_for_status()
        data = response.json()
    except httpx.RequestError:
        return result_page("Unable to reach the authentication service.", False)
    except httpx.HTTPStatusError as exc:
        try:
            data = exc.response.json()
        except ValueError:
            return result_page("Authentication service returned an error.", False)
        message = data.get("message") or "Authentication service returned an error."
        authenticated = bool(data.get("authenticated"))
        return result_page(message, authenticated)

    authenticated = bool(data.get("authenticated"))
    message = data.get("message") or "Authentication complete."
    return result_page(message, authenticated)
