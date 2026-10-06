"""Form validation. Registration rules that depend on the edition live in the services."""

import re
from typing import Annotated, Literal

from pydantic import BaseModel, EmailStr, Field, StringConstraints, field_validator

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=80)]
College = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=120)]

DEPARTMENTS = ["CSE", "IT", "ECE", "EEE", "EIE", "ICE", "MECH", "CIVIL", "PROD", "OTHER"]
HEARD_FROM = ["Instagram", "A friend", "SYNSARA website", "My college", "Other"]
Department = Literal["CSE", "IT", "ECE", "EEE", "EIE", "ICE", "MECH", "CIVIL", "PROD", "OTHER"]


def _mobile(value: str) -> str:
    digits = re.sub(r"[\s-]", "", value).removeprefix("+91")
    if not re.fullmatch(r"[6-9]\d{9}", digits):
        raise ValueError("enter a 10-digit Indian mobile number")
    return digits


class PersonDetails(BaseModel):
    name: Name
    college: College
    department: Department
    year: int = Field(ge=1, le=5)
    email: EmailStr
    mobile: str

    @field_validator("mobile")
    @classmethod
    def _check_mobile(cls, v: str) -> str:
        return _mobile(v)

    @field_validator("email")
    @classmethod
    def _lower(cls, v: str) -> str:
        return v.lower()


class EventRegistration(PersonDetails):
    technical: list[str] = []
    non_technical: list[str] = []


class HackathonRegistration(BaseModel):
    team_name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=60)]
    leader_name: Name
    college: College
    department: Department
    year: int = Field(ge=1, le=5)
    email: EmailStr
    mobile: str
    members: list[Name]
    project_title: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=3, max_length=120)
    ]
    domain: Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=60)]
    needs_technical_help: bool = False
    needs_accommodation: bool = False
    heard_from: Literal["Instagram", "A friend", "SYNSARA website", "My college", "Other"]

    @field_validator("mobile")
    @classmethod
    def _check_mobile(cls, v: str) -> str:
        return _mobile(v)

    @field_validator("email")
    @classmethod
    def _lower(cls, v: str) -> str:
        return v.lower()
