"""Real implementation: talks to the FastAPI backend through ``utils.api_client``.

Only routes that exist in the backend are used. What the backend cannot do yet (search, reviews,
book descriptions and ratings) is simply not advertised in ``supports`` and the UI hides it.
"""

from __future__ import annotations

from datetime import date

import streamlit as st

from data.errors import BusinessRuleError, DataUnavailable
from data.models import Book, LibraryEntry, Person, Profile, Review, Row
from data.repository import Repository
from data.search import filter_books
from utils.api_client import api_client


def _headers() -> dict:
    token = st.session_state.get("access_token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def _call(method: str, path: str, **kwargs):
    response = getattr(api_client, method)(path, headers=_headers(), **kwargs)
    status, data = response["status_code"], response["data"]
    if status == 0 or status in (401, 500, 502, 503):
        raise DataUnavailable(f"{status or 'network'}: {data}")
    if status in (400, 403, 404, 409, 422):
        detail = data.get("detail") if isinstance(data, dict) else data
        raise BusinessRuleError(str(detail))
    return data


def _book(raw: dict) -> Book:
    authors = tuple(a.strip() for a in (raw.get("authors") or "").split(",") if a.strip())
    return Book(
        work_id=raw["work_id"],
        title=raw.get("title") or "Sans titre",
        authors=authors,
        cover_url=raw.get("cover_url"),
        book_id=raw.get("book_id"),
    )


def _entry(raw: dict) -> LibraryEntry:
    return LibraryEntry(
        reading_id=raw["reading_id"],
        book=_book(raw["book"]),
        status=raw["status"],
        date_added=date.fromisoformat(raw["date_added"]),
        date_read=date.fromisoformat(raw["date_read"]) if raw.get("date_read") else None,
        rating=raw.get("rating"),
    )


class ApiRepository(Repository):
    source = "api"
    supports = frozenset({"social", "library"})

    @property
    def _user_id(self) -> int:
        return st.session_state["user_id"]

    # ---- catalogue ----------------------------------------------------------------------
    def catalog(self) -> list[Book]:
        return [_book(b) for b in _call("get", "/book/") or []]

    def featured(self) -> list[Book]:
        return self.catalog()[:4]

    def search(self, query="", genres=(), authors=(), sort="relevance") -> list[Book]:
        # GET /book/search is not available yet -> local filtering on the stored books
        return filter_books(self.catalog(), query, genres, authors, sort)

    def get_book(self, work_id: str) -> Book | None:
        try:
            return _book(_call("get", f"/book/{work_id}"))
        except BusinessRuleError:
            return None

    def book_reviews(self, work_id: str) -> list[Review]:
        return []  # no review route yet

    def home_rows(self) -> list[Row]:
        books = self.catalog()
        rows = []
        reading = [e.book for e in self.library("in progress")]
        if reading:
            rows.append(Row("continue", "Reprendre sa lecture", reading))
        if books:
            rows.append(Row("discover", "À découvrir", books))
        return rows

    # ---- library ------------------------------------------------------------------------
    def library(self, status: str | None = None) -> list[LibraryEntry]:
        params = {"status": status} if status else None
        raw = _call("get", f"/users/{self._user_id}/readings", params=params) or []
        return [_entry(r) for r in raw]

    def add_to_library(self, work_id: str, status: str = "to read") -> LibraryEntry:
        return _entry(_call("post", "/readings", json={"work_id": work_id, "status": status}))

    def set_status(self, work_id: str, status: str) -> LibraryEntry:
        entry = self.entry(work_id)
        if entry is None:
            raise BusinessRuleError("Ce livre n'est pas dans ta bibliothèque.")
        return _entry(_call("patch", f"/readings/{entry.reading_id}", json={"status": status}))

    def remove_from_library(self, work_id: str) -> None:
        entry = self.entry(work_id)
        if entry is not None:
            _call("delete", f"/readings/{entry.reading_id}")

    # ---- reviews & profile --------------------------------------------------------------
    def save_review(self, work_id: str, rating: int | None, text: str) -> None:
        entry = self.entry(work_id)
        if entry is None:
            raise BusinessRuleError("Ce livre n'est pas dans ta bibliothèque.")
        if rating is not None:
            _call("patch", f"/readings/{entry.reading_id}", json={"rating": rating})
        # the text of the review needs POST /readings/{id}/review (not implemented yet)

    def my_reviews(self) -> list[Review]:
        return []

    def profile(self) -> Profile:
        def people(path: str) -> tuple[Person, ...]:
            try:
                return tuple(
                    Person(p["username"], p["user_id"], p.get("bio")) for p in _call("get", path)
                )
            except (DataUnavailable, BusinessRuleError):
                return ()

        raw = _call("get", f"/user/{self._user_id}")
        return Profile(
            username=raw["username"],
            display_name=raw["username"],
            bio=raw.get("bio"),
            followers=people(f"/users/{self._user_id}/followers"),
            following=people(f"/users/{self._user_id}/following"),
        )
