"""Real implementation: talks to the FastAPI backend through ``utils.api_client``.

Only routes that exist in the backend are used. What the backend cannot do yet (search, reviews,
book descriptions and ratings) is simply not advertised in ``supports`` and the UI hides it.
"""

from __future__ import annotations

import re
from datetime import date

import streamlit as st

from auth import session
from data.errors import BusinessRuleError, DataUnavailable, NotFound
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
    if response["status_code"] == 0 and method == "get":  # stale keep-alive connection: reads are safe to retry once
        response = getattr(api_client, method)(path, headers=_headers(), **kwargs)
    status, data = response["status_code"], response["data"]
    if status == 401 and st.session_state.get("mode") == "api":
        session.expire()  # token expired or revoked: the user must log in again
        try:
            st.rerun()
        except Exception:  # not inside a script run (tests): fall through to the error below
            pass
    if status == 0 or status in (401, 500, 502, 503):
        raise DataUnavailable(f"{status or 'network'}: {data}")
    if status in (400, 403, 404, 409, 422):
        detail = data.get("detail") if isinstance(data, dict) else data
        raise (NotFound if status == 404 else BusinessRuleError)(str(detail))
    return data


def _book(raw: dict) -> Book:
    # the backend joins several authors with ", " (stored books) or " et " (OpenLibrary search)
    authors = tuple(a.strip() for a in re.split(r",| et ", raw.get("authors") or "") if a.strip())
    return Book(
        work_id=raw["work_id"],
        title=raw.get("title") or "Untitled",
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


def _liked_ids() -> set:
    """The backend does not tell which reviews the connected user already liked: remembered per session."""
    return st.session_state.setdefault("_liked_reviews", set())


def _review(raw: dict) -> Review:
    """Maps a ReviewReadModel of the backend (the book is nested, there is no rating on a review)."""
    book = raw.get("book") or {}
    created = raw.get("publication_date")
    return Review(
        review_id=raw["review_id"],
        work_id=book.get("work_id", ""),
        author=raw.get("username", ""),
        author_id=raw.get("user_id"),
        text=raw.get("text", ""),
        rating=raw.get("rating"),
        created=date.fromisoformat(created[:10]) if created else None,
        likes=raw.get("likes", 0),
        liked_by_me=raw["review_id"] in _liked_ids(),
        book_title=book.get("title"),
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
        # GET /books/ is the keyword search (q is required): the stored catalogue is GET /books/find_all/
        return [_book(b) for b in _call("get", "/books/find_all/") or []]

    def featured(self) -> list[Book]:
        return self.catalog()[:4]

    def _search_remote(self, query: str) -> list[Book]:
        """``GET /books?q=<query>`` (Search Books). Answers are kept for the session so that the reruns
        triggered by the filters do not call the backend again. 404 means "no result"."""
        cache = st.session_state.setdefault("_search_cache", {})
        key = query.casefold()
        if key in cache:
            return cache[key]
        try:
            raw = _call("get", "/books", params={"q": query})  # requests encodes spaces and special characters
        except NotFound:
            raw = []
        if not isinstance(raw, list):
            raise DataUnavailable("unexpected server response (a list of books was expected)")
        books = [_book(b) for b in raw if isinstance(b, dict) and b.get("work_id")]
        known = st.session_state.setdefault("_book_cache", {})
        known.update({b.work_id: b for b in books})  # results are not always stored in the database
        if len(cache) >= 30:
            cache.pop(next(iter(cache)))
        cache[key] = books
        return books

    def search(self, query="", genres=(), authors=(), sort="relevance") -> list[Book]:
        query = (query or "").strip()
        if not query:  # no keyword: the usual stored catalogue
            return filter_books(self.catalog(), "", genres, authors, sort)
        books = self._search_remote(query)
        if sort != "relevance":
            return filter_books(books, "", genres, authors, sort)
        wanted = set(authors)  # relevance = order given by the backend, kept as is
        return [b for b in books if not wanted or wanted.intersection(b.authors)]

    def get_book(self, work_id: str) -> Book | None:
        try:
            return _book(_call("get", f"/books/{work_id}"))
        except (BusinessRuleError, DataUnavailable) as exc:
            # 404: a search result is not necessarily stored in our database. 5xx / unreachable: the
            # details come from OpenLibrary; the book as listed (title, authors, cover) is still shown.
            known = st.session_state.get("_book_cache", {}).get(work_id)
            if known is None and isinstance(exc, DataUnavailable):
                try:
                    known = next((b for b in self.catalog() if b.work_id == work_id), None)
                except (BusinessRuleError, DataUnavailable):
                    known = None
                if known is None:
                    raise
            return known

    def book_reviews(self, work_id: str) -> list[Review]:
        if not backend_reviews_enabled():
            return []  # no review route in the backend yet
        return [_review(r) for r in _call("get", f"/review/books/{work_id}/reviews") or []]

    def home_rows(self) -> list[Row]:
        books = self.catalog()
        rows = []
        try:
            reading = [e.book for e in self.library("in progress")]
        except DataUnavailable:  # library route failing: the catalogue is still shown
            reading = []
        if reading:
            rows.append(Row("continue", "Continue Reading", reading))
        if books:
            rows.append(Row("discover", "Discover", books))
        return rows

    # ---- library ------------------------------------------------------------------------
    def library(self, status: str | None = None, user_id: int | None = None) -> list[LibraryEntry]:
        uid = self._user_id if user_id is None else user_id
        params = {"status": status} if status else None
        raw = _call("get", f"/users/{uid}/readings", params=params) or []
        return [_entry(r) for r in raw]

    def entry(self, work_id: str) -> LibraryEntry | None:
        try:
            return super().entry(work_id)
        except DataUnavailable:  # library route failing: the page must stay usable
            return None

    def add_to_library(self, work_id: str, status: str = "to read") -> LibraryEntry:
        return _entry(_call("post", "/readings", json={"work_id": work_id, "status": status}))

    def set_status(self, work_id: str, status: str) -> LibraryEntry:
        entry = self.entry(work_id)
        if entry is None:
            raise BusinessRuleError("This book is not in your library.")
        return _entry(_call("patch", f"/readings/{entry.reading_id}", json={"status": status}))

    def remove_from_library(self, work_id: str) -> None:
        entry = self.entry(work_id)
        if entry is not None:
            _call("delete", f"/readings/{entry.reading_id}")

    # ---- reviews & profile --------------------------------------------------------------
    def save_review(self, work_id: str, rating: int | None, text: str) -> None:
        entry = self.entry(work_id)
        if entry is None:
            raise BusinessRuleError("This book is not in your library.")
        if rating is not None:
            _call("patch", f"/readings/{entry.reading_id}", json={"rating": rating})
        if text.strip() and backend_reviews_enabled():
            path = f"/review/readings/{entry.reading_id}/review"
            try:
                _call("post", path, json={"text": text})
            except BusinessRuleError:  # 409: a review already exists for this reading -> edit it
                existing = _call("get", path)
                _call("put", f"/review/reviews/{existing['review_id']}", json={"text": text})

    def my_reviews(self) -> list[Review]:
        return self.user_reviews(None)

    def user_reviews(self, user_id: int | None = None) -> list[Review]:
        if not backend_reviews_enabled():
            return []
        uid = self._user_id if user_id is None else user_id
        return [_review(r) for r in _call("get", f"/review/users/{uid}/reviews") or []]

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
            raw = _call("get", f"/user/users/{uid}")  # user router is mounted under /user in main.py
        except BusinessRuleError:  # 404: unknown user
            return None
        # Only public fields are read: GET /user/users/{id} only returns public fields (no e-mail).
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
            raise BusinessRuleError("Likes are not available on the server yet.")
        path = f"/review/reviews/{review.review_id}/like"
        if review.liked_by_me:
            _call("delete", path)
            _liked_ids().discard(review.review_id)
        else:
            _call("put", path, json={"liked": True})
            _liked_ids().add(review.review_id)

    def is_following(self, user_id: int) -> bool:
        following = _call("get", f"/users/{self._user_id}/following") or []
        return any(p["user_id"] == user_id for p in following)

    def follow(self, user_id: int) -> None:
        _call("post", f"/users/{user_id}/follow")

    def unfollow(self, user_id: int) -> None:
        _call("delete", f"/users/{user_id}/follow")
