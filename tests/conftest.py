"""Test setup: a throwaway SQLite database and upload folder per test."""

import io
import os
import re
import tempfile
import zipfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="synsara-tests-"))
os.environ.update(
    DATABASE_URL=os.environ.get("TEST_DATABASE_URL", f"sqlite:///{_TMP / 'test.db'}"),
    UPLOAD_DIR=str(_TMP / "uploads"),
    SECRET_KEY="test-secret-key-not-for-production",
    ADMIN_USERNAME="admin",
    ADMIN_PASSWORD="test-admin-password",
    REGISTRATION_OPEN="true",
)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import models  # noqa: E402, F401
from app.core.config import get_settings  # noqa: E402
from app.db import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402

PDF = b"%PDF-1.4\n1 0 obj << >> endobj\ntrailer << >>\n%%EOF\n"


def make_docx() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("[Content_Types].xml", "<Types/>")
        zf.writestr("word/document.xml", "<w:document/>")
    return buf.getvalue()


@pytest.fixture(autouse=True)
def _fresh_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    settings = get_settings()
    original = settings.registration_open
    yield
    settings.registration_open = original


@pytest.fixture
def db():
    with SessionLocal() as session:
        yield session


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def csrf_of(client: TestClient, path: str) -> str:
    html = client.get(path).text
    match = re.search(r'name="csrf" value="([^"]+)"', html)
    assert match, f"no CSRF token on {path}"
    return match.group(1)


def person(**overrides) -> dict:
    data = {
        "name": "Asha Raman",
        "college": "Example Institute of Technology",
        "department": "CSE",
        "year": "3",
        "email": "asha@example.com",
        "mobile": "9876543210",
        "technical": ["code-fest"],
        "non_technical": ["shutter-snap"],
    }
    data.update(overrides)
    return data


def team(**overrides) -> dict:
    data = {
        "team_name": "Byte Busters",
        "leader_name": "Vikram Iyer",
        "college": "Example Institute of Technology",
        "department": "IT",
        "year": "2",
        "email": "vikram@example.com",
        "mobile": "9123456780",
        "members": ["Meena Das", "Rahul Nair"],
        "project_title": "Smart Bus Tracker",
        "domain": "IoT",
        "needs_technical_help": "yes",
        "heard_from": "A friend",
    }
    data.update(overrides)
    return data


def login(client: TestClient, password: str = "test-admin-password"):
    token = csrf_of(client, "/admin/login")
    return client.post(
        "/admin/login",
        data={"csrf": token, "username": "admin", "password": password, "next": "/admin"},
        follow_redirects=False,
    )
