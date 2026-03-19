import os

import httpx
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastui import AnyComponent, FastUI, components as c, prebuilt_html
from fastui.events import GoToEvent
from pydantic import BaseModel

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

app = FastAPI(title="Authentication UI")


class LoginForm(BaseModel):
    username: str
    passcode: str


class AuthResult(BaseModel):
    success: bool
    message: str


def login_page(error_message: str | None = None) -> list[AnyComponent]:
    components: list[AnyComponent] = [
        c.Heading(text="Sign in"),
    ]
    if error_message:
        components.append(c.Paragraph(text=error_message))

    components.append(
        c.Form(
            submit_url="/api/login",
            method="POST",
            form_fields=[
                c.FormFieldInput(name="username", title="Username", required=True),
                c.FormFieldInput(
                    name="passcode",
                    title="Passcode",
                    required=True,
                    html_type="password",
                ),
            ],
        )
    )

    return [c.Page(components=components)]


@app.get("/", response_class=HTMLResponse)
def read_index() -> str:
    return prebuilt_html(title="Authentication UI", api_root_url="/api")


@app.get("/api/", response_model=FastUI, response_model_exclude_none=True)
def read_login() -> list[AnyComponent]:
    return login_page()


@app.post("/api/login", response_model=FastUI, response_model_exclude_none=True)
def submit_login(form: LoginForm) -> list[AnyComponent]:
    try:
        response = httpx.post(
            f"{BACKEND_URL}/auth/login",
            json=form.model_dump(),
            timeout=5.0,
        )
    except httpx.RequestError:
        return login_page("Unable to reach authentication API.")

    if response.status_code == httpx.codes.OK:
        result = AuthResult.model_validate(response.json())
        return [
            c.Page(
                components=[
                    c.Heading(text="Welcome"),
                    c.Paragraph(text=result.message),
                    c.Button(text="Back to login", on_click=GoToEvent(url="/")),
                ]
            )
        ]

    return login_page("Invalid username or passcode.")
