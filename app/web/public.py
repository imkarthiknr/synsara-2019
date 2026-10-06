"""Public site: home, event pages, event registration, hackathon registration."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.content import Category, get_content
from app.core.config import get_settings
from app.db import get_db
from app.schemas import DEPARTMENTS, HEARD_FROM, EventRegistration, HackathonRegistration
from app.services import hackathon as hackathon_service
from app.services import registrations
from app.services.errors import RegistrationError
from app.web.common import field_errors, render, verify_csrf

router = APIRouter(include_in_schema=False)
DbSession = Annotated[Session, Depends(get_db)]


def _closed(request: Request):
    return render(request, "closed.html", status_code=status.HTTP_403_FORBIDDEN)


@router.get("/")
def home(request: Request):
    c = get_content()
    return render(
        request,
        "home.html",
        technical=c.by_category(Category.TECHNICAL),
        non_technical=c.by_category(Category.NON_TECHNICAL),
    )


@router.get("/events/{slug}")
def event_detail(slug: str, request: Request):
    c = get_content()
    if slug == c.hackathon.slug:
        return RedirectResponse("/hackathon", status.HTTP_301_MOVED_PERMANENTLY)
    event = c.event(slug)
    if event is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return render(request, "events/detail.html", event=event)


# ---------- event registration ----------


def _register_page(request: Request, values: dict, errors: dict, status_code: int = 200):
    c = get_content()
    return render(
        request,
        "register.html",
        status_code=status_code,
        values=values,
        errors=errors,
        dept_options=[(d, d) for d in DEPARTMENTS],
        technical=c.by_category(Category.TECHNICAL),
        non_technical=c.by_category(Category.NON_TECHNICAL),
    )


@router.get("/register")
def register_form(request: Request, event: str = ""):
    if not get_settings().registration_open:
        return _closed(request)
    values: dict = {"technical": [], "non_technical": []}
    chosen = get_content().event(event)
    if chosen:  # arriving from an event page pre-ticks that event
        key = "technical" if chosen.category == Category.TECHNICAL else "non_technical"
        values[key] = [chosen.slug]
    return _register_page(request, values, {})


@router.post("/register")
def register(
    request: Request,
    db: DbSession,
    csrf: Annotated[str, Form()] = "",
    name: Annotated[str, Form()] = "",
    college: Annotated[str, Form()] = "",
    department: Annotated[str, Form()] = "",
    year: Annotated[str, Form()] = "",
    email: Annotated[str, Form()] = "",
    mobile: Annotated[str, Form()] = "",
    technical: Annotated[list[str], Form()] = [],  # noqa: B006
    non_technical: Annotated[list[str], Form()] = [],  # noqa: B006
):
    verify_csrf(request, csrf)
    if not get_settings().registration_open:
        return _closed(request)
    values = {
        "name": name,
        "college": college,
        "department": department,
        "year": year,
        "email": email,
        "mobile": mobile,
        "technical": technical,
        "non_technical": non_technical,
    }
    try:
        data = EventRegistration.model_validate(values)
        participant = registrations.register(db, get_content(), data)
    except ValidationError as exc:
        return _register_page(request, values, field_errors(exc), 422)
    except RegistrationError as exc:
        return _register_page(request, values, {exc.field: exc.message}, 422)
    request.session["registered"] = participant.id
    return RedirectResponse("/register/done", status.HTTP_303_SEE_OTHER)


@router.get("/register/done")
def register_done(request: Request, db: DbSession):
    pid = request.session.get("registered")
    participant = registrations.get_participant(db, pid) if pid else None
    if participant is None:
        return RedirectResponse("/register", status.HTTP_303_SEE_OTHER)
    c = get_content()
    events = [c.event(e.event_slug) for e in participant.entries]
    return render(
        request, "register_done.html", participant=participant, events=[e for e in events if e]
    )


# ---------- hackathon ----------


@router.get("/hackathon")
def hackathon(request: Request):
    return render(request, "hackathon/index.html")


def _hack_page(request: Request, values: dict, errors: dict, status_code: int = 200):
    return render(
        request,
        "hackathon/register.html",
        status_code=status_code,
        values=values,
        errors=errors,
        dept_options=[(d, d) for d in DEPARTMENTS],
        heard_options=[(h, h) for h in HEARD_FROM],
    )


@router.get("/hackathon/register")
def hackathon_form(request: Request):
    if not get_settings().registration_open:
        return _closed(request)
    return _hack_page(request, {"members": []}, {})


@router.post("/hackathon/register")
async def hackathon_register(
    request: Request,
    db: DbSession,
    csrf: Annotated[str, Form()] = "",
    team_name: Annotated[str, Form()] = "",
    leader_name: Annotated[str, Form()] = "",
    college: Annotated[str, Form()] = "",
    department: Annotated[str, Form()] = "",
    year: Annotated[str, Form()] = "",
    email: Annotated[str, Form()] = "",
    mobile: Annotated[str, Form()] = "",
    members: Annotated[list[str], Form()] = [],  # noqa: B006
    project_title: Annotated[str, Form()] = "",
    domain: Annotated[str, Form()] = "",
    needs_technical_help: Annotated[str | None, Form()] = None,
    needs_accommodation: Annotated[str | None, Form()] = None,
    heard_from: Annotated[str, Form()] = "",
    abstract: Annotated[UploadFile | None, File()] = None,
):
    verify_csrf(request, csrf)
    if not get_settings().registration_open:
        return _closed(request)
    members = [m.strip() for m in members if m.strip()]
    values = {
        "team_name": team_name,
        "leader_name": leader_name,
        "college": college,
        "department": department,
        "year": year,
        "email": email,
        "mobile": mobile,
        "members": members,
        "project_title": project_title,
        "domain": domain,
        "needs_technical_help": needs_technical_help == "yes",
        "needs_accommodation": needs_accommodation == "yes",
        "heard_from": heard_from,
    }
    max_bytes = get_settings().max_upload_mb * 1024 * 1024
    content_bytes = await abstract.read(max_bytes + 1) if abstract and abstract.filename else b""
    try:
        data = HackathonRegistration.model_validate(values)
        team = hackathon_service.register_team(
            db, get_content(), data, abstract.filename if abstract else "", content_bytes
        )
    except ValidationError as exc:
        return _hack_page(request, values, field_errors(exc), 422)
    except RegistrationError as exc:
        return _hack_page(request, values, {exc.field: exc.message}, 422)
    request.session["team"] = team.id
    return RedirectResponse("/hackathon/register/done", status.HTTP_303_SEE_OTHER)


@router.get("/hackathon/register/done")
def hackathon_done(request: Request, db: DbSession):
    tid = request.session.get("team")
    team = hackathon_service.get_team(db, tid) if tid else None
    if team is None:
        return RedirectResponse("/hackathon/register", status.HTTP_303_SEE_OTHER)
    return render(request, "hackathon/done.html", team=team)
