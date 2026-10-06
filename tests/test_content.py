from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from app.content import Category, get_content, load_content


def test_edition_content_loads():
    c = get_content()
    assert c.edition.title == "SYNSARA 2K19"
    assert c.event_count == 9
    assert [e.slug for e in c.by_category(Category.TECHNICAL)] == [
        "code-fest",
        "code-relay",
        "paper-presentation",
        "inovate",
    ]
    assert len(c.by_category(Category.NON_TECHNICAL)) == 3


def test_event_logos_and_template_exist():
    static = Path(__file__).parents[1] / "app" / "static"
    c = get_content()
    for e in c.events:
        if e.logo:
            assert (static / "img" / e.logo).is_file(), e.logo
    assert (static / c.hackathon.abstract_template).is_file()


def test_duplicate_slugs_are_rejected(tmp_path):
    src = Path(__file__).parents[1] / "content" / "synsara-2019.yaml"
    data = yaml.safe_load(src.read_text(encoding="utf-8"))
    data["events"][1]["slug"] = data["events"][0]["slug"]
    bad = tmp_path / "bad.yaml"
    bad.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(ValidationError):
        load_content(bad)
