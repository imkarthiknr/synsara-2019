"""ORM models. Event slugs come from the content file, so they're stored as strings."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Participant(Base):
    """One person registered for one or more (non-hackathon) events."""

    __tablename__ = "participants"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    college: Mapped[str] = mapped_column(String(120))
    department: Mapped[str] = mapped_column(String(40))
    year: Mapped[int] = mapped_column(Integer)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    mobile: Mapped[str] = mapped_column(String(10), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    entries: Mapped[list[EventEntry]] = relationship(
        back_populates="participant", cascade="all, delete-orphan", order_by="EventEntry.id"
    )

    @property
    def code(self) -> str:
        return f"SYN19-{self.id:04d}"


class EventEntry(Base):
    __tablename__ = "event_entries"
    __table_args__ = (UniqueConstraint("participant_id", "event_slug"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    participant_id: Mapped[int] = mapped_column(
        ForeignKey("participants.id", ondelete="CASCADE"), index=True
    )
    event_slug: Mapped[str] = mapped_column(String(40), index=True)

    participant: Mapped[Participant] = relationship(back_populates="entries")


class HackathonTeam(Base):
    __tablename__ = "hackathon_teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    team_name: Mapped[str] = mapped_column(String(60), unique=True)
    leader_name: Mapped[str] = mapped_column(String(80))
    college: Mapped[str] = mapped_column(String(120))
    department: Mapped[str] = mapped_column(String(40))
    year: Mapped[int] = mapped_column(Integer)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    mobile: Mapped[str] = mapped_column(String(10), unique=True)
    project_title: Mapped[str] = mapped_column(String(120))
    domain: Mapped[str] = mapped_column(String(60))
    needs_technical_help: Mapped[bool] = mapped_column(Boolean, default=False)
    needs_accommodation: Mapped[bool] = mapped_column(Boolean, default=False)
    heard_from: Mapped[str] = mapped_column(String(40))
    abstract_path: Mapped[str] = mapped_column(String(80))
    abstract_filename: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    members: Mapped[list[TeamMember]] = relationship(
        back_populates="team", cascade="all, delete-orphan", order_by="TeamMember.position"
    )

    @property
    def code(self) -> str:
        return f"HUM19-{self.id:03d}"


class TeamMember(Base):
    """Members other than the leader (names only, as in the original form)."""

    __tablename__ = "team_members"

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(
        ForeignKey("hackathon_teams.id", ondelete="CASCADE"), index=True
    )
    position: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(80))

    team: Mapped[HackathonTeam] = relationship(back_populates="members")
