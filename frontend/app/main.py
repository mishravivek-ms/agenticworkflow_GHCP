from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastui import FastUI, prebuilt_html
from fastui import components as c
from fastui import events

from app.models.auth import LoginRequest
from app.services.auth_service import authenticate_user

app = FastAPI(title="Authentication UI")

c.Form.model_rebuild(_types_namespace={"AnyComponent": c.AnyComponent})
c.ModelForm.model_rebuild(_types_namespace={"AnyComponent": c.AnyComponent})


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return prebuilt_html(title="Authentication UI")


@app.get("/api/", response_model=FastUI, response_model_exclude_none=True)
def login_form() -> list[c.AnyComponent]:
    return [
        c.Page(
            components=[
                c.Heading(text="Sign in"),
                c.ModelForm(model=LoginRequest, submit_url="/api/login"),
            ]
        )
    ]


@app.post("/api/login", response_model=FastUI, response_model_exclude_none=True)
async def login(payload: LoginRequest) -> list[c.AnyComponent]:
    result = await authenticate_user(payload)
    status = "Success" if result.success else "Failed"

    return [
        c.Page(
            components=[
                c.Heading(text=f"Login {status}"),
                c.Paragraph(text=result.message),
                c.Link(
                    components=[c.Text(text="Back to login")],
                    on_click=events.GoToEvent(url="/api/"),
                ),
            ]
        )
    ]
