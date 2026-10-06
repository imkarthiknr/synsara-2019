"""Event registration: the 2019 rules (max 2 technical + 2 non-technical, hackathon exclusive)."""

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.content import Category, Content
from app.models import EventEntry, HackathonTeam, Participant
from app.schemas import EventRegistration
from app.services.errors import RegistrationError


def _validate_choices(content: Content, data: EventRegistration) -> list[str]:
    rules = content.rules
    tech = list(dict.fromkeys(data.technical))
    non_tech = list(dict.fromkeys(data.non_technical))
    valid_tech = {e.slug for e in content.by_category(Category.TECHNICAL)}
    valid_non = {e.slug for e in content.by_category(Category.NON_TECHNICAL)}
    if not set(tech) <= valid_tech:
        raise RegistrationError("Choose technical events from the list.", "technical")
    if not set(non_tech) <= valid_non:
        raise RegistrationError("Choose non-technical events from the list.", "non_technical")
    if len(tech) > rules.max_technical:
        raise RegistrationError(
            f"You can take part in at most {rules.max_technical} technical events.", "technical"
        )
    if len(non_tech) > rules.max_non_technical:
        raise RegistrationError(
            f"You can take part in at most {rules.max_non_technical} non-technical events.",
            "non_technical",
        )
    if not tech and not non_tech:
        raise RegistrationError("Pick at least one event.", "events")
    return tech + non_tech


def email_in_hackathon(db: Session, email: str) -> bool:
    return db.scalar(select(HackathonTeam.id).where(HackathonTeam.email == email)) is not None


def register(db: Session, content: Content, data: EventRegistration) -> Participant:
    slugs = _validate_choices(content, data)
    if db.scalar(select(Participant.id).where(func.lower(Participant.email) == data.email)):
        raise RegistrationError("This e-mail is already registered.", "email")
    if db.scalar(select(Participant.id).where(Participant.mobile == data.mobile)):
        raise RegistrationError("This mobile number is already registered.", "mobile")
    if content.rules.hackathon_is_exclusive and email_in_hackathon(db, data.email):
        name = content.hackathon.name
        raise RegistrationError(
            f"You've registered for {name}, so you can't take part in other events.", "email"
        )
    participant = Participant(
        name=data.name,
        college=data.college,
        department=data.department,
        year=data.year,
        email=data.email,
        mobile=data.mobile,
        entries=[EventEntry(event_slug=s) for s in slugs],
    )
    db.add(participant)
    try:
        db.commit()
    except IntegrityError as exc:  # race with a concurrent registration
        db.rollback()
        raise RegistrationError("This e-mail or mobile number is already registered.") from exc
    db.refresh(participant)
    return participant


def get_participant(db: Session, participant_id: int) -> Participant | None:
    return db.scalar(
        select(Participant)
        .options(selectinload(Participant.entries))
        .where(Participant.id == participant_id)
    )


def list_participants(db: Session, event_slug: str | None = None, q: str = "") -> list[Participant]:
    stmt = select(Participant).options(selectinload(Participant.entries))
    if event_slug:
        stmt = stmt.join(EventEntry).where(EventEntry.event_slug == event_slug)
    if q:
        like = "%" + q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
        stmt = stmt.where(
            Participant.name.ilike(like, escape="\\")
            | Participant.email.ilike(like, escape="\\")
            | Participant.college.ilike(like, escape="\\")
            | Participant.mobile.ilike(like, escape="\\")
        )
    return list(db.scalars(stmt.order_by(Participant.id)).unique().all())


def counts_by_event(db: Session) -> dict[str, int]:
    rows = db.execute(
        select(EventEntry.event_slug, func.count(EventEntry.id)).group_by(EventEntry.event_slug)
    ).all()
    return {slug: int(n) for slug, n in rows}


def delete_participant(db: Session, participant: Participant) -> None:
    db.delete(participant)
    db.commit()
