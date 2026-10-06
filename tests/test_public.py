from app.core.config import get_settings
from tests.conftest import PDF, csrf_of, person, team


def test_pages_render(client):
    for path in ["/", "/events/code-fest", "/register", "/hackathon", "/hackathon/register"]:
        r = client.get(path)
        assert r.status_code == 200, path
    assert "Code Fest" in client.get("/").text


def test_unknown_event_is_404(client):
    r = client.get("/events/nope")
    assert r.status_code == 404
    assert "text/html" in r.headers["content-type"]


def test_hackathon_slug_redirects(client):
    r = client.get("/events/hack-una-matata", follow_redirects=False)
    assert r.status_code == 301
    assert r.headers["location"] == "/hackathon"


def test_register_prefills_event(client):
    html = client.get("/register?event=code-relay").text
    assert 'value="code-relay" checked' in html


def test_security_headers(client):
    r = client.get("/")
    assert r.headers["x-frame-options"] == "DENY"
    assert r.headers["x-content-type-options"] == "nosniff"
    assert "default-src 'self'" in r.headers["content-security-policy"]
    assert client.get("/health").json() == {"status": "ok"}


def test_register_success(client):
    token = csrf_of(client, "/register")
    r = client.post("/register", data={"csrf": token, **person()}, follow_redirects=True)
    assert r.status_code == 200
    assert "SYN19-0001" in r.text
    assert "Code Fest" in r.text


def test_register_requires_csrf(client):
    client.get("/register")
    r = client.post("/register", data={"csrf": "wrong", **person()})
    assert r.status_code == 400


def test_register_validation_errors(client):
    token = csrf_of(client, "/register")
    r = client.post("/register", data={"csrf": token, **person(email="nope", mobile="12345")})
    assert r.status_code == 422
    assert "Asha Raman" in r.text  # values are kept


def test_duplicate_email_is_rejected(client):
    token = csrf_of(client, "/register")
    client.post("/register", data={"csrf": token, **person()})
    r = client.post(
        "/register",
        data={"csrf": token, **person(email="ASHA@example.com", mobile="9876500000")},
    )
    assert r.status_code == 422
    assert "already registered" in r.text


def test_registration_closed(client):
    get_settings().registration_open = False
    assert "closed" in client.get("/register").text.lower()
    token = csrf_of(client, "/admin/login")
    r = client.post("/register", data={"csrf": token, **person()})
    assert "closed" in r.text.lower()


def test_hackathon_register_success(client):
    token = csrf_of(client, "/hackathon/register")
    r = client.post(
        "/hackathon/register",
        data={"csrf": token, **team()},
        files={"abstract": ("idea.pdf", PDF, "application/pdf")},
        follow_redirects=True,
    )
    assert r.status_code == 200
    assert "HUM19-001" in r.text


def test_hackathon_rejects_non_document(client):
    token = csrf_of(client, "/hackathon/register")
    r = client.post(
        "/hackathon/register",
        data={"csrf": token, **team()},
        files={"abstract": ("idea.pdf", b"MZ not a pdf", "application/pdf")},
    )
    assert r.status_code == 422
    assert "PDF or Word" in r.text


def test_hackathon_and_events_are_exclusive(client):
    token = csrf_of(client, "/hackathon/register")
    client.post(
        "/hackathon/register",
        data={"csrf": token, **team()},
        files={"abstract": ("idea.pdf", PDF, "application/pdf")},
    )
    r = client.post("/register", data={"csrf": token, **person(email="vikram@example.com")})
    assert r.status_code == 422
    assert "hackathon" in r.text.lower()
