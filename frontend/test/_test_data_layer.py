import pytest
import streamlit as st

from auth import session
from data import demo_catalog
from data.demo_repository import DemoRepository
from data.errors import BusinessRuleError
from data.factory import FallbackRepository, get_repository
from data.search import filter_books, normalize


@pytest.fixture
def repo():
    return DemoRepository()


def test_demo_ids_never_look_like_open_library_ids():
    assert all(wid.startswith("demo-") for wid in demo_catalog.books())


def test_search_ignores_accents_and_case():
    books = demo_catalog.books().values()
    assert [b.title for b in filter_books(books, "ETRANGER")] == ["L'Étranger"]
    assert normalize("Étranger") == "etranger"


def test_search_filters_and_sorts():
    books = list(demo_catalog.books().values())
    scifi = filter_books(books, genres=["Science-fiction"], sort="title")
    assert scifi and all("Science-fiction" in b.genres for b in scifi)
    assert [b.title for b in scifi] == sorted((b.title for b in scifi), key=normalize)


def test_add_then_change_status(repo):
    work = "demo-atomic-habits"
    assert repo.entry(work) is None
    repo.add_to_library(work)
    assert repo.entry(work).status == "to read"
    repo.set_status(work, "read")
    assert repo.entry(work).status == "read"
    assert repo.entry(work).date_read is not None


def test_cannot_add_twice(repo):
    repo.add_to_library("demo-atomic-habits")
    with pytest.raises(BusinessRuleError):
        repo.add_to_library("demo-atomic-habits")


def test_rating_requires_read_or_abandoned(repo):
    repo.add_to_library("demo-atomic-habits", "in progress")
    with pytest.raises(BusinessRuleError):
        repo.save_review("demo-atomic-habits", 4, "Super")
    repo.set_status("demo-atomic-habits", "read")
    repo.save_review("demo-atomic-habits", 4, "Super")
    assert repo.entry("demo-atomic-habits").rating == 4
    assert any(r.text == "Super" for r in repo.my_reviews())


def test_demo_login_is_isolated_and_logout_clears_everything():
    session.demo_login()
    assert session.is_logged_in() and session.is_demo()
    assert "access_token" not in st.session_state
    assert isinstance(get_repository(), DemoRepository)
    get_repository().add_to_library("demo-atomic-habits")
    session.logout()
    assert not session.is_logged_in() and "demo_state" not in st.session_state


def test_api_down_falls_back_to_demo_catalogue(monkeypatch):
    monkeypatch.setattr(
        "data.api_repository.api_client",
        type("Down", (), {"get": lambda *a, **k: {"status_code": 0, "data": "Connection error"}})(),
    )
    monkeypatch.setenv("EXLIBRIS_DATA_SOURCE", "auto")
    repo = FallbackRepository()
    assert len(repo.catalog()) > 10
    assert repo.degraded and repo.source == "api"


def test_api_only_mode_never_uses_demo_books(monkeypatch):
    monkeypatch.setattr(
        "data.api_repository.api_client",
        type("Down", (), {"get": lambda *a, **k: {"status_code": 0, "data": "x"}})(),
    )
    monkeypatch.setenv("EXLIBRIS_DATA_SOURCE", "api")
    assert FallbackRepository().catalog() == []
