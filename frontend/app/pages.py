from __future__ import annotations

from fastui import components as c
from fastui.events import GoToEvent


def login_page(error: str | None = None, success: str | None = None) -> list[c.AnyComponent]:
    """Return FastUI components for the login page.

    Banners are driven by query-string params so the page can be reached
    via a plain redirect without requiring server-side session state.
    """
    components: list[c.AnyComponent] = [
        c.Heading(text="Sign In", level=2),
    ]

    if error:
        components.append(
            c.Div(
                components=[c.Text(text=error)],
                class_name="alert alert-danger",
            )
        )

    if success:
        components.append(
            c.Div(
                components=[c.Text(text=success)],
                class_name="alert alert-success",
            )
        )

    components.append(
        c.Form(
            submit_url="/api/login",
            form_fields=[
                c.FormFieldInput(
                    name="username",
                    title="Username",
                    required=True,
                    placeholder="Enter your username",
                ),
                c.FormFieldInput(
                    name="passcode",
                    title="Passcode",
                    required=True,
                    html_type="password",
                    placeholder="Enter your passcode",
                ),
            ],
            footer=[c.Button(text="Sign In", html_type="submit")],
        )
    )

    return [c.Page(components=components)]


def dashboard_page() -> list[c.AnyComponent]:
    """Return FastUI components for the dashboard page shown after successful login."""
    return [
        c.Page(
            components=[
                c.Heading(text="Dashboard", level=1),
                c.Paragraph(text="You are successfully authenticated."),
                c.Paragraph(text="Welcome! You now have access to protected resources."),
                c.Div(
                    components=[
                        c.Button(
                            text="Log Out",
                            on_click=GoToEvent(url="/"),
                        ),
                    ],
                    class_name="mt-3",
                ),
            ]
        )
    ]
