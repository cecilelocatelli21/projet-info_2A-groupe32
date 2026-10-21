"""Demo implementation: fictitious data, state kept in ``st.session_state['demo_state']``.

Nothing here ever reaches the backend. Rules that the real backend enforces (rating only for
'read'/'abandoned' readings, one reading per book) are mirrored so the demo behaves the same way.
"""

from __future__ import annotations

import zlib
from dataclasses import replace
from datetime import date

import streamlit as st

from data import demo_catalog
from data.errors import BusinessRuleError
from data.models import (
    RATING_STATUSES,
    STATUSES,
    Book,
    LibraryEntry,
    Profile,
    Review,
    Row,
)
from data.repository import Repository
from data.search import filter_books

_STATE_KEY = "demo_state"


class DemoCatalog:
    """Read-only demo catalogue (no session state): also used as the API catalogue fallback."""

    def __init__(self):
        self._books = demo_catalog.books()

    def featured(self) -> list[Book]:
        return [self._books[demo_catalog.wid(s)] for s in demo_catalog.FEATURED_SLUGS]

    def catalog(self) -> list[Book]:
        return list(self._books.values())

    def get_book(self, work_id: str) -> Book | None:
        return self._books.get(work_id)

    def search(self, query="", genres=(), authors=(), sort="relevance") -> list[Book]:
        return filter_books(self.catalog(), query, genres, authors, sort)

    def book_reviews(self, work_id: str) -> list[Review]:
        return demo_catalog.other_reviews(work_id)


class DemoRepository(Repository):
    source = "demo"
    supports = frozenset(
        {"search", "reviews", "details", "social", "recommendations", "likes", "follow", "library"}
    )

    def __init__(self):
        self._catalog = DemoCatalog()

    # ---- session state ------------------------------------------------------------------
    @property
    def _state(self) -> dict:
        if _STATE_KEY not in st.session_state:
            st.session_state[_STATE_KEY] = {
                "entries": demo_catalog.initial_library(),
                "reviews": demo_catalog.initial_my_reviews(),
                "likes": set(),  # ids of the reviews liked by the demo user
                "following": demo_catalog.initial_following(),
                "next_reading_id": 1000,
            }
        return st.session_state[_STATE_KEY]

    def reset(self) -> None:
        st.session_state.pop(_STATE_KEY, None)

    # ---- catalogue ----------------------------------------------------------------------
    def featured(self) -> list[Book]:
        return self._catalog.featured()

    def catalog(self) -> list[Book]:
        return self._catalog.catalog()

    def get_book(self, work_id: str) -> Book | None:
        return self._catalog.get_book(work_id)

    def search(self, query="", genres=(), authors=(), sort="relevance") -> list[Book]:
        return self._catalog.search(query, genres, authors, sort)

    def book_reviews(self, work_id: str) -> list[Review]:
        reviews = self._catalog.book_reviews(work_id)
        mine = self._state["reviews"].get(work_id)
        return [self._with_likes(r) for r in ([mine] if mine else []) + reviews]

    def _with_likes(self, review: Review) -> Review:
        """Adds the demo user's own like to the stored (fictitious) counter."""
        if review.is_mine or review.review_id not in self._state["likes"]:
            return review
        return replace(review, likes=review.likes + 1, liked_by_me=True)

    # ---- home rows ----------------------------------------------------------------------
    def _affinities(self) -> dict[str, float]:
        """Genre -> affinity score from the user's library (used for the recommendations)."""
        scores: dict[str, float] = {}
        for entry in self._state["entries"].values():
            if entry.status == "read":
                weight = (entry.rating or 3) - 2
            elif entry.status == "abandoned":
                weight = -0.5
            else:
                weight = 1
            for genre in entry.book.genres:
                scores[genre] = scores.get(genre, 0) + weight
        return scores

    def home_rows(self) -> list[Row]:
        entries = self._state["entries"]
        in_library = set(entries)
        books = self.catalog()
        rows: list[Row] = []

        reading = [e.book for e in self.library("in progress")]
        if reading:
            rows.append(Row("continue", "Continue Reading", reading))

        affinities = self._affinities()
        candidates = [b for b in books if b.work_id not in in_library]
        ranked = sorted(
            candidates,
            key=lambda b: (-(sum(affinities.get(g, 0) for g in b.genres) + (b.rating or 0) / 10)),
        )
        top_genres = [g for g, _ in sorted(affinities.items(), key=lambda kv: -kv[1])[:2]]
        subtitle = ("Based on your reading: " + " and ".join(top_genres).lower()) if top_genres else None
        rows.append(Row("reco", "Our Recommendations", ranked[:14], subtitle))

        rows.append(
            Row(
                "popular",
                "Must-Reads",
                sorted(books, key=lambda b: -b.ratings_count)[:14],
            )
        )
        rows.append(
            Row(
                "top",
                "Top Rated",
                sorted(books, key=lambda b: (-(b.rating or 0), -b.ratings_count))[:14],
            )
        )
        shuffled = sorted(candidates, key=lambda b: zlib.crc32(b.work_id.encode()))
        rows.append(Row("discover", "Discover", shuffled[:14]))
        rows.append(
            Row(
                "recent",
                "Latest Discoveries",
                sorted(books, key=lambda b: -(b.published or 0))[:14],
            )
        )
        return rows

    # ---- library ------------------------------------------------------------------------
    @property
    def own_id(self) -> int:
        return demo_catalog.DEMO_USER_ID

    def library(self, status: str | None = None, user_id: int | None = None) -> list[LibraryEntry]:
        if user_id is not None and user_id != self.own_id:
            others = demo_catalog.user_library(user_id)
            return [e for e in others if status is None or e.status == status]
        entries = list(self._state["entries"].values())
        if status:
            entries = [e for e in entries if e.status == status]
        return sorted(entries, key=lambda e: e.date_added, reverse=True)

    def entry(self, work_id: str) -> LibraryEntry | None:
        return self._state["entries"].get(work_id)

    def add_to_library(self, work_id: str, status: str = "to read") -> LibraryEntry:
        book = self.get_book(work_id)
        if book is None:
            raise BusinessRuleError(f"Book with work_id '{work_id}' not found")
        if status not in STATUSES:
            raise BusinessRuleError(f"Unknown status '{status}'")
        if work_id in self._state["entries"]:
            raise BusinessRuleError("This book is already in the user's library")
        self._state["next_reading_id"] += 1
        entry = LibraryEntry(
            reading_id=self._state["next_reading_id"],
            book=book,
            status=status,
            date_added=date.today(),
            date_read=date.today() if status == "read" else None,
        )
        self._state["entries"][work_id] = entry
        return entry

    def set_status(self, work_id: str, status: str) -> LibraryEntry:
        entry = self._state["entries"].get(work_id)
        if entry is None:
            raise BusinessRuleError(f"Book '{work_id}' is not in the library")
        if status not in STATUSES:
            raise BusinessRuleError(f"Unknown status '{status}'")
        date_read = entry.date_read
        if status == "read" and date_read is None:
            date_read = date.today()
        updated = replace(entry, status=status, date_read=date_read)
        self._state["entries"][work_id] = updated
        return updated

    def remove_from_library(self, work_id: str) -> None:
        self._state["entries"].pop(work_id, None)
        self._state["reviews"].pop(work_id, None)

    # ---- reviews & profile --------------------------------------------------------------
    def save_review(self, work_id: str, rating: int | None, text: str) -> None:
        entry = self._state["entries"].get(work_id)
        if entry is None:
            raise BusinessRuleError(f"Book '{work_id}' is not in the library")
        if entry.status not in RATING_STATUSES:
            raise BusinessRuleError(
                "A rating can only be given to a reading with status 'read' or 'abandoned'"
            )
        if rating is not None:
            self._state["entries"][work_id] = replace(entry, rating=rating)
        text = (text or "").strip()
        if text:
            previous = self._state["reviews"].get(work_id)
            self._state["reviews"][work_id] = Review(
                review_id=previous.review_id if previous else 3000 + len(self._state["reviews"]),
                work_id=work_id,
                author=demo_catalog.DEMO_DISPLAY_NAME,
                text=text,
                rating=rating if rating is not None else entry.rating,
                created=date.today(),
                likes=previous.likes if previous else 0,
                book_title=entry.book.title,
                is_mine=True,
            )

    def my_reviews(self) -> list[Review]:
        reviews = list(self._state["reviews"].values())
        return sorted(reviews, key=lambda r: r.created or date.min, reverse=True)

    def user_reviews(self, user_id: int | None = None) -> list[Review]:
        if user_id is None or user_id == self.own_id:
            return self.my_reviews()
        return [self._with_likes(r) for r in demo_catalog.reviews_by_author(user_id)]

    def profile(self, user_id: int | None = None) -> Profile | None:
        uid = self.own_id if user_id is None else user_id
        return demo_catalog.user_profile(uid, self._state["following"])

    # ---- likes & follows ----------------------------------------------------------------
    def toggle_like(self, review: Review) -> None:
        known = {r.review_id: r for r in self._all_reviews()}
        stored = known.get(review.review_id)
        if stored is None:
            raise BusinessRuleError(f"Review {review.review_id} not found")
        if stored.is_mine:
            raise BusinessRuleError("You cannot like your own review")
        self._state["likes"].symmetric_difference_update({review.review_id})

    def _all_reviews(self) -> list[Review]:
        found = list(self._state["reviews"].values())
        for slug in demo_catalog.REVIEWED_SLUGS:
            found += demo_catalog.other_reviews(demo_catalog.wid(slug))
        return found

    def is_following(self, user_id: int) -> bool:
        return user_id in self._state["following"]

    def follow(self, user_id: int) -> None:
        if user_id == self.own_id or demo_catalog.person(user_id) is None:
            raise BusinessRuleError("Invalid user to follow")
        self._state["following"].add(user_id)

    def unfollow(self, user_id: int) -> None:
        self._state["following"].discard(user_id)
