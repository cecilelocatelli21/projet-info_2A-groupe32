"""The contract between the UI and the data, plus the factory that picks the data source.

The views only talk to a :class:`Repository`. Two implementations exist:

* ``DemoRepository`` (data/demo_repository.py): fictitious data kept in the Streamlit session.
* ``ApiRepository``  (data/api_repository.py): the real backend, through ``utils.api_client``.

Demo and real data are never merged: a demo session only sees demo data. The one exception is the
read-only *catalogue* fallback (see ``FallbackRepository``), which is flagged in the UI.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from data.models import Book, LibraryEntry, Profile, Review, Row


class Repository(ABC):
    #: "demo" or "api" -> shown in the UI so the audience knows what they are looking at
    source: str = "demo"
    #: True when part of the data comes from the demo fallback because the API failed
    degraded: bool = False
    degraded_reason: str | None = None
    #: optional capabilities the data source implements (the UI hides what is missing)
    supports: frozenset[str] = frozenset()

    # ---- catalogue ----------------------------------------------------------------------
    @abstractmethod
    def featured(self) -> list[Book]: ...

    @abstractmethod
    def catalog(self) -> list[Book]: ...

    @abstractmethod
    def search(
        self, query: str = "", genres=(), authors=(), sort: str = "relevance"
    ) -> list[Book]: ...

    @abstractmethod
    def get_book(self, work_id: str) -> Book | None: ...

    @abstractmethod
    def book_reviews(self, work_id: str) -> list[Review]: ...

    @abstractmethod
    def home_rows(self) -> list[Row]: ...

    def genres(self) -> list[str]:
        return sorted({g for b in self.catalog() for g in b.genres})

    def authors(self) -> list[str]:
        return sorted({a for b in self.catalog() for a in b.authors})

    # ---- library ------------------------------------------------------------------------
    @abstractmethod
    def library(self, status: str | None = None, user_id: int | None = None) -> list[LibraryEntry]:
        """Library of ``user_id`` (default: the connected user). Public: no follow needed."""

    @property
    @abstractmethod
    def own_id(self) -> int | None:
        """Id of the connected user."""

    def entry(self, work_id: str) -> LibraryEntry | None:
        return next((e for e in self.library() if e.book.work_id == work_id), None)

    @abstractmethod
    def add_to_library(self, work_id: str, status: str = "to read") -> LibraryEntry: ...

    @abstractmethod
    def set_status(self, work_id: str, status: str) -> LibraryEntry: ...

    @abstractmethod
    def remove_from_library(self, work_id: str) -> None: ...

    # ---- reviews & profile --------------------------------------------------------------
    @abstractmethod
    def save_review(self, work_id: str, rating: int | None, text: str) -> None: ...

    def update_review(self, review: Review, rating: int | None, text: str) -> None:
        """Edit the connected user's own review in place (text and, when it changed, the rating)."""
        raise NotImplementedError

    @abstractmethod
    def my_reviews(self) -> list[Review]: ...

    @abstractmethod
    def user_reviews(self, user_id: int | None = None) -> list[Review]:
        """Public reviews written by ``user_id`` (default: the connected user)."""

    @abstractmethod
    def profile(self, user_id: int | None = None) -> Profile | None:
        """Public profile of ``user_id`` (default: the connected user); None if unknown."""

    # ---- likes & follows (independent from the visibility of a profile) ---------------------
    @abstractmethod
    def toggle_like(self, review: Review) -> None:
        """Like the review, or remove the like if already liked."""

    @abstractmethod
    def is_following(self, user_id: int) -> bool: ...

    @abstractmethod
    def follow(self, user_id: int) -> None: ...

    @abstractmethod
    def unfollow(self, user_id: int) -> None: ...

    def search_users(self, username: str = "") -> list:
        """Public users whose username contains ``username`` (needs the "user_search" capability)."""
        return []

    def reset(self) -> None:  # only meaningful for the demo
        return None
