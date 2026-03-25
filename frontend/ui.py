from __future__ import annotations

from typing import Annotated

from fastui import AnyComponent
from fastui import components as c
from pydantic import BaseModel, Field, SecretStr


class LoginForm(BaseModel):
    username: Annotated[str, Field(title="Username")]
    password: Annotated[SecretStr, Field(title="Password")]


def login_page() -> list[AnyComponent]:
    return [
        c.Page(
            components=[
                c.Heading(text="Login", level=1),
                c.ModelForm(
                    model=LoginForm,
                    submit_url="/api/login",
                    submit_text="Sign In",
                ),
            ]
        )
    ]
