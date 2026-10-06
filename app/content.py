"""Edition content (events, dates, rules) loaded and validated from YAML."""

from datetime import date
from enum import StrEnum
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, model_validator

from app.core.config import get_settings


class Category(StrEnum):
    TECHNICAL = "technical"
    NON_TECHNICAL = "non_technical"


class Edition(BaseModel):
    name: str
    year_label: str
    tagline: str
    host: str
    institution: str
    city: str
    venue_url: str | None = None
    starts_on: date
    ends_on: date
    prize_pool_inr: int
    expected_participants: int | None = None
    contact_email: str
    about: str

    @property
    def title(self) -> str:
        return f"{self.name} {self.year_label}"


class Rules(BaseModel):
    max_technical: int = Field(ge=0)
    max_non_technical: int = Field(ge=0)
    hackathon_is_exclusive: bool = True
    hackathon_team_min: int = Field(ge=1)
    hackathon_team_max: int = Field(ge=1)


class Event(BaseModel):
    slug: str = Field(pattern=r"^[a-z0-9-]+$")
    name: str
    category: Category
    logo: str | None = None
    teaser: str
    team: str
    description: str
    rounds: list[str] = []
    rules: list[str] = []


class Faq(BaseModel):
    q: str
    a: str


class Hackathon(BaseModel):
    slug: str
    name: str
    logo: str | None = None
    teaser: str
    description: str
    abstract_template: str | None = None
    faqs: list[Faq] = []


class Workshop(BaseModel):
    name: str
    teaser: str


class Sponsor(BaseModel):
    name: str
    url: str | None = None
    logo: str | None = None


class Content(BaseModel):
    edition: Edition
    rules: Rules
    events: list[Event]
    hackathon: Hackathon
    workshop: Workshop | None = None
    sponsors: list[Sponsor] = []

    @model_validator(mode="after")
    def _unique_slugs(self) -> "Content":
        slugs = [e.slug for e in self.events] + [self.hackathon.slug]
        if len(slugs) != len(set(slugs)):
            raise ValueError("event slugs must be unique")
        return self

    def event(self, slug: str) -> Event | None:
        return next((e for e in self.events if e.slug == slug), None)

    def by_category(self, category: Category) -> list[Event]:
        return [e for e in self.events if e.category == category]

    @property
    def event_count(self) -> int:
        return len(self.events) + 1 + (1 if self.workshop else 0)


def load_content(path: Path) -> Content:
    with path.open(encoding="utf-8") as fh:
        return Content.model_validate(yaml.safe_load(fh))


@lru_cache
def get_content() -> Content:
    return load_content(get_settings().content_file)
