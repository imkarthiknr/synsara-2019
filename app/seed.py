"""Load fictional demo registrations: `python -m app.seed`.

Every name, e-mail and number here is made up. Running it twice does nothing the
second time, because the e-mails are already registered.
"""

import logging

from app.content import get_content
from app.db import SessionLocal
from app.schemas import EventRegistration, HackathonRegistration
from app.services import hackathon, registrations
from app.services.errors import RegistrationError

log = logging.getLogger("synsara.seed")

# name, college, department, year, technical events, non-technical events
PEOPLE = [
    (
        "Ananya Iyer",
        "Lakeview Institute of Technology",
        "CSE",
        3,
        ["code-fest", "code-relay"],
        ["cric-bizz"],
    ),
    ("Karan Mehta", "Lakeview Institute of Technology", "IT", 2, ["code-fest"], ["shutter-snap"]),
    ("Divya Prakash", "Hillside College of Engineering", "ECE", 4, ["paper-presentation"], []),
    (
        "Rohit Sharma",
        "Hillside College of Engineering",
        "CSE",
        3,
        ["inovate", "code-fest"],
        ["blitz-brigade"],
    ),
    (
        "Fathima Noor",
        "Riverbend Engineering College",
        "IT",
        2,
        ["code-relay"],
        ["shutter-snap", "cric-bizz"],
    ),
    (
        "Arvind Kumar",
        "Riverbend Engineering College",
        "MECH",
        3,
        [],
        ["cric-bizz", "blitz-brigade"],
    ),
    ("Sneha Pillai", "Coastal Institute of Science", "CSE", 1, ["code-fest"], []),
    (
        "Vignesh Babu",
        "Coastal Institute of Science",
        "EEE",
        4,
        ["paper-presentation", "inovate"],
        [],
    ),
    (
        "Priya Nair",
        "Lakeview Institute of Technology",
        "CSE",
        2,
        ["code-relay", "inovate"],
        ["shutter-snap"],
    ),
    ("Harish Raj", "Northgate Polytechnic University", "ECE", 3, ["code-fest"], ["blitz-brigade"]),
    (
        "Lakshmi Menon",
        "Northgate Polytechnic University",
        "IT",
        4,
        ["paper-presentation"],
        ["shutter-snap"],
    ),
    ("Sanjay Gupta", "Hillside College of Engineering", "CIVIL", 1, [], ["cric-bizz"]),
]

TEAMS = [
    (
        "Null Pointers",
        "Nikhil Varma",
        ["Aisha Khan", "Tarun Bose", "Meghna Rao"],
        "CampusCart",
        "E-commerce",
    ),
    (
        "Byte Brigade",
        "Ishita Sen",
        ["Rahul Jain", "Kavya Reddy"],
        "Clean Streets Tracker",
        "Civic tech",
    ),
]

DEMO_PDF = b"%PDF-1.4\n% SYNSARA demo abstract\n1 0 obj << >> endobj\ntrailer << >>\n%%EOF\n"


def _email(name: str) -> str:
    return name.lower().replace(" ", ".") + "@example.com"


def seed() -> tuple[int, int]:
    content = get_content()
    added_people = added_teams = 0
    with SessionLocal() as db:
        for i, (name, college, dept, year, tech, non_tech) in enumerate(PEOPLE):
            data = EventRegistration(
                name=name,
                college=college,
                department=dept,
                year=year,
                email=_email(name),
                mobile=f"70000{i:05d}",
                technical=tech,
                non_technical=non_tech,
            )
            try:
                registrations.register(db, content, data)
                added_people += 1
            except RegistrationError:
                pass
        for i, (team_name, leader, members, title, domain) in enumerate(TEAMS):
            data = HackathonRegistration(
                team_name=team_name,
                leader_name=leader,
                college="Riverbend Engineering College",
                department="CSE",
                year=3,
                email=_email(leader),
                mobile=f"80000{i:05d}",
                members=members,
                project_title=title,
                domain=domain,
                heard_from="SYNSARA website",
            )
            try:
                hackathon.register_team(db, content, data, f"{title} abstract.pdf", DEMO_PDF)
                added_teams += 1
            except RegistrationError:
                pass
    return added_people, added_teams


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    people, teams = seed()
    log.info("Added %d demo participants and %d demo teams.", people, teams)
