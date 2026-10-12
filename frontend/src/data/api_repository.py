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
from utils.settings import backend_reviews_enabled


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


def _review(raw: dict) -> Review:
    """Maps a review of the backend. The review routes are not implemented yet: the field names
    below follow the planned ReviewReadModel (doc/Ex-Libris — Endpoints de l'API.md) and must be
    checked against the real response once the routes exist."""
    created = raw.get("publication_date") or raw.get("created")
    return Review(
        review_id=raw["review_id"],
        work_id=raw.get("work_id", ""),
        author=raw.get("username", ""),
        author_id=raw.get("user_id"),
        text=raw.get("text", ""),
        rating=raw.get("rating"),
        created=date.fromisoformat(created[:10]) if created else None,
        likes=raw.get("likes", 0),
        liked_by_me=bool(raw.get("liked_by_me", False)),
        book_title=raw.get("book_title"),
        is_mine=raw.get("user_id") == st.session_state.get("user_id"),
    )


class ApiRepository(Repository):
    source = "api"

    @property
    def supports(self) -> frozenset[str]:  # type: ignore[override]
        base = {"social", "library", "follow"}
        return frozenset(base | ({"reviews", "likes"} if backend_reviews_enabled() else set()))

    @property
    def _user_id(self) -> int:
        return st.session_state["user_id"]

    @property
    def own_id(self) -> int:
        return self._user_id

    # ---- catalogue ----------------------------------------------------------------------
    def catalog(self) -> list[Book]:
        return [_book(b) for b in _call("get", "/books/") or []]

    def featured(self) -> list[Book]:
        return self.catalog()[:4]

    def search(self, query="", genres=(), authors=(), sort="relevance") -> list[Book]:
        # GET /books?q= exists but returns OpenLibrary results (not the stored catalogue) -> local filtering on the stored books
        return filter_books(self.catalog(), query, genres, authors, sort)

    def get_book(self, work_id: str) -> Book | None:
        try:
            return _book(_call("get", f"/books/{work_id}"))
        except BusinessRuleError:
            return None

    def book_reviews(self, work_id: str) -> list[Review]:
        if not backend_reviews_enabled():
            return []  # no review route in the backend yet
        return [_review(r) for r in _call("get", f"/books/{work_id}/reviews") or []]

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
    def library(self, status: str | None = None, user_id: int | None = None) -> list[LibraryEntry]:
        uid = self._user_id if user_id is None else user_id
        params = {"status": status} if status else None
        raw = _call("get", f"/users/{uid}/readings", params=params) or []
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
        return self.user_reviews(None)

    def user_reviews(self, user_id: int | None = None) -> list[Review]:
        if not backend_reviews_enabled():
            return []
        uid = self._user_id if user_id is None else user_id
        return [_review(r) for r in _call("get", f"/users/{uid}/reviews") or []]

    def profile(self, user_id: int | None = None) -> Profile | None:
        uid = self._user_id if user_id is None else user_id

        def people(path: str) -> tuple[Person, ...]:
            try:
                return tuple(
                    Person(p["username"], p["user_id"], p.get("bio")) for p in _call("get", path) or []
                )
            except (DataUnavailable, BusinessRuleError):
                return ()

        try:
            raw = _call("get", f"/user/{uid}")
        except BusinessRuleError:  # 404: unknown user
            return None
        # Only public fields are read: GET /user/{id} also returns the e-mail, never displayed.
        return Profile(
            user_id=uid,
            username=raw["username"],
            display_name=raw["username"],
            bio=raw.get("bio"),
            followers=people(f"/users/{uid}/followers"),
            following=people(f"/users/{uid}/following"),
        )

    # ---- likes & follows ----------------------------------------------------------------
    def toggle_like(self, review: Review) -> None:
        if not backend_reviews_enabled():
            raise BusinessRuleError("Les likes ne sont pas encore disponibles sur le serveur.")
        path = f"/reviews/{review.review_id}/like"
        if review.liked_by_me:
            _call("delete", path)
        else:
            _call("put", path, json={"liked": True})

    def is_following(self, user_id: int) -> bool:
        following = _call("get", f"/users/{self._user_id}/following") or []
        return any(p["user_id"] == user_id for p in following)

    def follow(self, user_id: int) -> None:
        _call("post", f"/users/{user_id}/follow")

    def unfollow(self, user_id: int) -> None:
        _call("delete", f"/users/{user_id}/follow")
