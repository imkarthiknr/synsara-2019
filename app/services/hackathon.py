"""Hackathon team registration with a validated abstract upload."""

import secrets
import zipfile
from io import BytesIO
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.content import Content
from app.core.config import get_settings
from app.models import HackathonTeam, Participant, TeamMember
from app.schemas import HackathonRegistration
from app.services.errors import RegistrationError

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def sniff_abstract(data: bytes) -> str:
    """Return 'pdf' or 'docx' by content (not file name), or raise RegistrationError."""
    if data.startswith(b"%PDF-"):
        return "pdf"
    if data.startswith(b"PK\x03\x04"):
        try:
            with zipfile.ZipFile(BytesIO(data)) as zf:
                if "word/document.xml" in zf.namelist():
                    return "docx"
        except zipfile.BadZipFile:
            pass
    raise RegistrationError("Upload your abstract as a PDF or Word (.docx) file.", "abstract")


def _safe_display_name(filename: str, ext: str) -> str:
    stem = Path(filename or "abstract").stem
    stem = "".join(c for c in stem if c.isalnum() or c in " -_.")[:80].strip() or "abstract"
    return f"{stem}.{ext}"


def register_team(
    db: Session, content: Content, data: HackathonRegistration, filename: str, abstract: bytes
) -> HackathonTeam:
    rules = content.rules
    members = [m for m in data.members if m]
    size = 1 + len(members)
    if not rules.hackathon_team_min <= size <= rules.hackathon_team_max:
        raise RegistrationError(
            f"Teams need {rules.hackathon_team_min} to {rules.hackathon_team_max} members "
            "including the leader.",
            "members",
        )
    settings = get_settings()
    if not abstract:
        raise RegistrationError("Attach your project abstract.", "abstract")
    if len(abstract) > settings.max_upload_mb * 1024 * 1024:
        raise RegistrationError(
            f"The abstract must be smaller than {settings.max_upload_mb} MB.", "abstract"
        )
    ext = sniff_abstract(abstract)

    if db.scalar(
        select(HackathonTeam.id).where(
            func.lower(HackathonTeam.team_name) == data.team_name.lower()
        )
    ):
        raise RegistrationError("That team name is taken. Pick another one.", "team_name")
    if db.scalar(select(HackathonTeam.id).where(HackathonTeam.email == data.email)):
        raise RegistrationError("This e-mail has already registered a team.", "email")
    if db.scalar(select(HackathonTeam.id).where(HackathonTeam.mobile == data.mobile)):
        raise RegistrationError("This mobile number has already registered a team.", "mobile")
    if rules.hackathon_is_exclusive and db.scalar(
        select(Participant.id).where(Participant.email == data.email)
    ):
        raise RegistrationError(
            "This e-mail is registered for other events. Hackathon teams can't take part in them.",
            "email",
        )

    stored_name = f"{secrets.token_hex(16)}.{ext}"
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    path = settings.upload_dir / stored_name
    path.write_bytes(abstract)

    team = HackathonTeam(
        team_name=data.team_name,
        leader_name=data.leader_name,
        college=data.college,
        department=data.department,
        year=data.year,
        email=data.email,
        mobile=data.mobile,
        project_title=data.project_title,
        domain=data.domain,
        needs_technical_help=data.needs_technical_help,
        needs_accommodation=data.needs_accommodation,
        heard_from=data.heard_from,
        abstract_path=stored_name,
        abstract_filename=_safe_display_name(filename, ext),
        members=[TeamMember(position=i + 1, name=n) for i, n in enumerate(members)],
    )
    db.add(team)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        path.unlink(missing_ok=True)
        raise RegistrationError(
            "This team, e-mail or mobile number is already registered."
        ) from exc
    db.refresh(team)
    return team


def get_team(db: Session, team_id: int) -> HackathonTeam | None:
    return db.scalar(
        select(HackathonTeam)
        .options(selectinload(HackathonTeam.members))
        .where(HackathonTeam.id == team_id)
    )


def list_teams(db: Session) -> list[HackathonTeam]:
    return list(
        db.scalars(
            select(HackathonTeam)
            .options(selectinload(HackathonTeam.members))
            .order_by(HackathonTeam.id)
        ).all()
    )


def abstract_file(team: HackathonTeam) -> Path:
    path = (get_settings().upload_dir / team.abstract_path).resolve()
    if path.parent != get_settings().upload_dir.resolve():  # defence in depth
        raise FileNotFoundError(team.abstract_path)
    return path


def delete_team(db: Session, team: HackathonTeam) -> None:
    path = get_settings().upload_dir / team.abstract_path
    db.delete(team)
    db.commit()
    path.unlink(missing_ok=True)
