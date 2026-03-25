from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastui import AnyComponent, prebuilt_html
from fastui import components as c
from fastui.events import PageEvent

from app.models import LoginRequest

router = APIRouter()


@router.get("/api/ui/{path:path}")
@router.get("/api/ui/", include_in_schema=False)
async def ui_root(path: str = "") -> list[AnyComponent]:
    return [
        c.Page(
            components=[
                c.Heading(text="Sign In", level=1),
                c.ModelForm(
                    model=LoginRequest,
                    submit_url="/api/login",
                    loading=[c.Spinner(text="Signing in…")],
                    footer=[],
                    submit_trigger=PageEvent(name="form-submit"),
                ),
            ]
        )
    ]


@router.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    """Serve the FastUI single-page application shell."""
    return HTMLResponse(prebuilt_html(title="Sign In"))
