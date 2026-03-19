"""
FastUI frontend application.

This server renders the UI using FastUI components and proxies API calls
to the FastAPI backend running on port 8000.
"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastui import FastUI, AnyComponent, prebuilt_html
from fastui import components as c
from fastui.events import GoToEvent
import httpx

BACKEND_URL = "http://localhost:8000/api/v1"

app = FastAPI(title="AgenticWorkflow UI")


async def _fetch_items() -> list[dict]:
    """Fetch items from the backend API."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/items/")
        response.raise_for_status()
        return response.json()


@app.get("/api/", response_model=FastUI, response_model_exclude_none=True)
async def root_page() -> list[AnyComponent]:
    """Render the home page."""
    return [
        c.Page(
            components=[
                c.Heading(text="AgenticWorkflow", level=1),
                c.Paragraph(text="Welcome to the AgenticWorkflow application."),
                c.Button(
                    text="View Items",
                    on_click=GoToEvent(url="/items/"),
                ),
            ]
        )
    ]


@app.get("/api/items/", response_model=FastUI, response_model_exclude_none=True)
async def items_page() -> list[AnyComponent]:
    """Render the items list page."""
    try:
        items = await _fetch_items()
    except httpx.HTTPError:
        items = []

    rows = [
        c.Div(
            components=[
                c.Text(text=f"#{item['id']} — {item['name']}"),
                c.Text(text=f"  ${item['price']:.2f}"),
            ]
        )
        for item in items
    ]

    return [
        c.Page(
            components=[
                c.Heading(text="Items", level=2),
                c.Button(text="← Back", on_click=GoToEvent(url="/")),
                *(rows if rows else [c.Paragraph(text="No items found.")]),
            ]
        )
    ]


@app.get("/{path:path}")
async def html_landing() -> HTMLResponse:
    """Serve the FastUI prebuilt HTML shell for all other routes."""
    return HTMLResponse(prebuilt_html(title="AgenticWorkflow"))
