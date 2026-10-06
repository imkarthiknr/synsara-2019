"""Organiser console: login, dashboard, participants, hackathon teams and exports."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import FileResponse, RedirectResponse, Response
from sqlalchemy.orm import Session

from app.content import get_content
from app.core.security import check_admin_credentials, is_admin
from app.db import get_db
from app.services import exports, registrations
from app.services import hackathon as hackathon_service
from app.web.common import flash, render, verify_csrf

router = APIRouter(prefix="/admin", include_in_schema=False)
DbSession = Annotated[Session, Depends(get_db)]
XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class NotAdmin(Exception):
    pass


def require_admin(request: Request) -> None:
    if not is_admin(request):
        raise NotAdmin


Admin = Depends(require_admin)


def _attachment(data: bytes | str, media_type: str, filename: str) -> Response:
    return Response(
        data,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
        },
    )


@router.get("/login")
def login_form(request: Request, next: str = "/admin"):
    if is_admin(request):
        return RedirectResponse("/admin", status.HTTP_303_SEE_OTHER)
    return render(request, "admin/login.html", next=_safe_next(next), error=None, username="")


def _safe_next(url: str | None) -> str:
    return url if url and url.startswith("/admin") and not url.startswith("//") else "/admin"


@router.post("/login")
def login(
    request: Request,
    csrf: Annotated[str, Form()] = "",
    username: Annotated[str, Form()] = "",
    password: Annotated[str, Form()] = "",
    next: Annotated[str, Form()] = "/admin",
):
    verify_csrf(request, csrf)
    if not check_admin_credentials(username, password):
        return render(
            request,
            "admin/login.html",
            status_code=401,
            next=_safe_next(next),
            error="Incorrect username or password.",
            username=username,
        )
    request.session.clear()
    request.session["admin"] = True
    return RedirectResponse(_safe_next(next), status.HTTP_303_SEE_OTHER)


@router.post("/logout")
def logout(request: Request, csrf: Annotated[str, Form()] = ""):
    verify_csrf(request, csrf)
    request.session.clear()
    return RedirectResponse("/", status.HTTP_303_SEE_OTHER)


@router.get("", dependencies=[Admin])
def dashboard(request: Request, db: DbSession):
    c = get_content()
    counts = registrations.counts_by_event(db)
    participants = registrations.list_participants(db)
    teams = hackathon_service.list_teams(db)
    return render(
        request,
        "admin/dashboard.html",
        counts=counts,
        participants=participants,
        teams=teams,
        recent=list(reversed(participants))[:5],
        events=c.events,
    )


@router.get("/participants", dependencies=[Admin])
def participants(request: Request, db: DbSession, event: str = "", q: str = ""):
    c = get_content()
    if event and c.event(event) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    rows = registrations.list_participants(db, event or None, q.strip()[:80])
    return render(request, "admin/participants.html", rows=rows, event=event, q=q, events=c.events)


@router.post("/participants/{pid}/delete", dependencies=[Admin])
def delete_participant(
    pid: int, request: Request, db: DbSession, csrf: Annotated[str, Form()] = ""
):
    verify_csrf(request, csrf)
    p = registrations.get_participant(db, pid)
    if p is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    registrations.delete_participant(db, p)
    flash(request, f"Deleted {p.code} ({p.name}).")
    return RedirectResponse("/admin/participants", status.HTTP_303_SEE_OTHER)


@router.get("/teams", dependencies=[Admin])
def teams(request: Request, db: DbSession):
    return render(request, "admin/teams.html", teams=hackathon_service.list_teams(db))


@router.get("/teams/{tid}", dependencies=[Admin])
def team_detail(tid: int, request: Request, db: DbSession):
    team = hackathon_service.get_team(db, tid)
    if team is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return render(request, "admin/team.html", team=team)


@router.get("/teams/{tid}/abstract", dependencies=[Admin])
def team_abstract(tid: int, db: DbSession):
    team = hackathon_service.get_team(db, tid)
    if team is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    try:
        path = hackathon_service.abstract_file(team)
    except FileNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND) from exc
    if not path.exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    media = "application/pdf" if path.suffix == ".pdf" else hackathon_service.DOCX_MIME
    return FileResponse(
        path,
        media_type=media,
        filename=f"{team.code}-{team.abstract_filename}",
        headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
    )


@router.post("/teams/{tid}/delete", dependencies=[Admin])
def delete_team(tid: int, request: Request, db: DbSession, csrf: Annotated[str, Form()] = ""):
    verify_csrf(request, csrf)
    team = hackathon_service.get_team(db, tid)
    if team is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    hackathon_service.delete_team(db, team)
    flash(request, f"Deleted team {team.team_name}.")
    return RedirectResponse("/admin/teams", status.HTTP_303_SEE_OTHER)


@router.get("/export.xlsx", dependencies=[Admin])
def export_all(db: DbSession):
    c = get_content()
    data = exports.workbook(
        c, registrations.list_participants(db), hackathon_service.list_teams(db)
    )
    return _attachment(data, XLSX, f"synsara-registrations-{date.today()}.xlsx")


@router.get("/export/{slug}.xlsx", dependencies=[Admin])
def export_event(slug: str, db: DbSession):
    c = get_content()
    event = c.event(slug)
    if event is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    data = exports.event_workbook(c, event.name, registrations.list_participants(db, slug))
    return _attachment(data, XLSX, f"synsara-{slug}-{date.today()}.xlsx")


@router.get("/participants.csv", dependencies=[Admin])
def export_csv(db: DbSession):
    c = get_content()
    return _attachment(
        exports.participants_csv(c, registrations.list_participants(db)),
        "text/csv",
        f"synsara-participants-{date.today()}.csv",
    )
