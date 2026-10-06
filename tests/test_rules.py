import pytest

from app.content import get_content
from app.core.config import get_settings
from app.schemas import EventRegistration, HackathonRegistration
from app.services import hackathon, registrations
from app.services.errors import RegistrationError
from tests.conftest import PDF, make_docx, person, team


def reg(**overrides) -> EventRegistration:
    return EventRegistration.model_validate(person(**overrides))


def hack(**overrides) -> HackathonRegistration:
    data = team(**overrides)
    data["needs_technical_help"] = data.get("needs_technical_help") == "yes"
    return HackathonRegistration.model_validate(data)


@pytest.mark.parametrize("raw", ["98765 43210", "+91 98765-43210", "9876543210"])
def test_mobile_is_normalised(raw):
    assert reg(mobile=raw).mobile == "9876543210"


def test_mobile_must_be_indian():
    with pytest.raises(ValueError):
        reg(mobile="1234567890")


def test_codes(db):
    p = registrations.register(db, get_content(), reg())
    assert p.code == "SYN19-0001"


def test_needs_an_event(db):
    with pytest.raises(RegistrationError, match="at least one"):
        registrations.register(db, get_content(), reg(technical=[], non_technical=[]))


def test_category_limits(db):
    with pytest.raises(RegistrationError, match="2"):
        registrations.register(
            db, get_content(), reg(technical=["code-fest", "code-relay", "inovate"])
        )


def test_unknown_or_wrong_category_event(db):
    with pytest.raises(RegistrationError):
        registrations.register(db, get_content(), reg(technical=["shutter-snap"]))
    with pytest.raises(RegistrationError):
        registrations.register(db, get_content(), reg(technical=["hack-una-matata"]))


def test_duplicate_mobile(db):
    registrations.register(db, get_content(), reg())
    with pytest.raises(RegistrationError) as exc:
        registrations.register(db, get_content(), reg(email="other@example.com"))
    assert exc.value.field == "mobile"


def test_counts_and_search(db):
    c = get_content()
    registrations.register(db, c, reg())
    registrations.register(
        db, c, reg(name="Ravi Kumar", email="ravi@example.com", mobile="9000000001")
    )
    counts = registrations.counts_by_event(db)
    assert counts["code-fest"] == 2
    assert [p.name for p in registrations.list_participants(db, q="ravi")] == ["Ravi Kumar"]
    assert registrations.list_participants(db, q="%") == []  # LIKE wildcards are escaped


def test_sniffing():
    assert hackathon.sniff_abstract(PDF) == "pdf"
    assert hackathon.sniff_abstract(make_docx()) == "docx"
    for bad in [b"", b"PK\x03\x04broken", b"<html>"]:
        with pytest.raises(RegistrationError):
            hackathon.sniff_abstract(bad)


def test_team_size(db):
    with pytest.raises(RegistrationError, match="3 to 5"):
        hackathon.register_team(db, get_content(), hack(members=["Solo Member"]), "a.pdf", PDF)
    with pytest.raises(RegistrationError, match="3 to 5"):
        members = [f"Member {i}" for i in range(5)]
        hackathon.register_team(db, get_content(), hack(members=members), "a.pdf", PDF)


def test_upload_size_limit(db):
    big = PDF + b"0" * (get_settings().max_upload_mb * 1024 * 1024)
    with pytest.raises(RegistrationError, match="smaller"):
        hackathon.register_team(db, get_content(), hack(), "a.pdf", big)


def test_team_saves_file_and_deletes_it(db):
    t = hackathon.register_team(db, get_content(), hack(), "../../etc/My Idea!.pdf", PDF)
    assert t.code == "HUM19-001"
    assert t.abstract_filename == "My Idea.pdf"
    path = hackathon.abstract_file(t)
    assert path.read_bytes() == PDF
    assert path.parent == get_settings().upload_dir.resolve()
    hackathon.delete_team(db, t)
    assert not path.exists()


def test_team_duplicates(db):
    c = get_content()
    hackathon.register_team(db, c, hack(), "a.pdf", PDF)
    with pytest.raises(RegistrationError) as exc:
        hackathon.register_team(
            db,
            c,
            hack(team_name="BYTE busters", email="x@example.com", mobile="9000000002"),
            "a.pdf",
            PDF,
        )
    assert exc.value.field == "team_name"
    with pytest.raises(RegistrationError) as exc:
        hackathon.register_team(
            db, c, hack(team_name="Other Team", mobile="9000000002"), "a.pdf", PDF
        )
    assert exc.value.field == "email"


def test_event_participant_cannot_join_hackathon(db):
    c = get_content()
    registrations.register(db, c, reg(email="vikram@example.com", mobile="9000000003"))
    with pytest.raises(RegistrationError, match=r"(?i)hackathon|events"):
        hackathon.register_team(db, c, hack(), "a.pdf", PDF)
