"""Template setup, CSRF, flash messages and form-error helpers shared by public and admin routes."""

import secrets
from datetime import date
from pathlib import Path

from fastapi import HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from app.content import get_content
from app.core.config import get_settings

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


def _inr(value: int) -> str:
    """Indian digit grouping: 100000 -> 1,00,000."""
    s = str(int(value))
    if len(s) <= 3:
        return s
    head, tail = s[:-3], s[-3:]
    groups = []
    while len(head) > 2:
        groups.insert(0, head[-2:])
        head = head[:-2]
    if head:
        groups.insert(0, head)
    return ",".join(groups) + "," + tail


templates.env.filters["inr"] = _inr
templates.env.globals["today"] = date.today


def csrf_token(request: Request) -> str:
    token = request.session.get("csrf")
    if not token:
        token = secrets.token_urlsafe(24)
        request.session["csrf"] = token
    return token


def verify_csrf(request: Request, submitted: str | None) -> None:
    expected = request.session.get("csrf")
    if not expected or not submitted or not secrets.compare_digest(expected, submitted):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Your session expired. Reload the page and try again."
        )


def flash(request: Request, message: str, kind: str = "ok") -> None:
    request.session["flash"] = {"message": message, "kind": kind}


def render(request: Request, name: str, status_code: int = 200, **ctx):
    flash_msg = request.session.pop("flash", None)
    return templates.TemplateResponse(
        request,
        name,
        {
            "c": get_content(),
            "settings": get_settings(),
            "csrf": csrf_token(request),
            "flash": flash_msg,
            "is_admin": request.session.get("admin") is True,
            **ctx,
        },
        status_code=status_code,
    )


def _friendly(err: dict) -> str:
    kind, ctx = err["type"], err.get("ctx") or {}
    if kind in ("missing", "string_too_short") and not err.get("input"):
        return "This field is required."
    if kind == "string_too_short":
        return f"Must be at least {ctx.get('min_length')} characters."
    if kind == "string_too_long":
        return f"Must be at most {ctx.get('max_length')} characters."
    if kind == "literal_error":
        return "Choose one of the options."
    if kind in ("int_parsing", "greater_than_equal", "less_than_equal"):
        return "Choose one of the options."
    if kind == "value_error" and err["loc"] and err["loc"][0] == "email":
        return "Enter a valid e-mail address."
    msg = str(err["msg"]).removeprefix("Value error, ")
    return msg[:1].upper() + msg[1:] + ("" if msg.endswith(".") else ".")


def field_errors(exc: ValidationError) -> dict[str, str]:
    out: dict[str, str] = {}
    for err in exc.errors():
        field = str(err["loc"][0]) if err["loc"] else "form"
        out.setdefault(field, _friendly(dict(err)))
    return out
