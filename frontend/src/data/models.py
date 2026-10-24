"""Plain data structures shared by the UI, the demo data and the API adapter.

They mirror the backend contracts (``BookModel``, ``ReadingReadModel``...) and add the optional
fields the UI would like to show (description, genres, rating...). Every extra field is optional:
the UI must cope with its absence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

# Same vocabulary as the backend (schema/reading_model.py)
STATUSES = ("to read", "in progress", "read", "abandoned")
# The backend values are also the labels shown to the user (same four words everywhere in the UI).
STATUS_LABELS = {status: status for status in STATUSES}
# Business rule (reading_service.update_reading): rating and review need a final status
RATING_STATUSES = ("read", "abandoned")


@dataclass(frozen=True)
class Edition:
    """One edition of a work (``EditionModel`` of ``GET /books/{work_id}``); every field may be missing."""

    title: str | None = None
    publisher: str | None = None
    publish_date: str | None = None
    pages: int | None = None
    isbn: str | None = None

    @property
    def is_empty(self) -> bool:
        return not any((self.title, self.publisher, self.publish_date, self.pages, self.isbn))


@dataclass(frozen=True)
class Book:
    work_id: str
    title: str
    authors: tuple[str, ...] = ()
    cover_url: str | None = None
    description: str | None = None
    genres: tuple[str, ...] = ()
    rating: float | None = None
    ratings_count: int = 0
    published: int | None = None
    pages: int | None = None
    publisher: str | None = None
    isbn: str | None = None
    book_id: int | None = None
    is_demo: bool = False
    #: Open Library details (``GET /books/{work_id}``): True once they have been received
    detailed: bool = False
    editions: tuple[Edition, ...] = ()

    @property
    def authors_label(self) -> str:
        return ", ".join(self.authors) if self.authors else "Unknown author"

    @property
    def main_genre(self) -> str | None:
        return self.genres[0] if self.genres else None


@dataclass(frozen=True)
class LibraryEntry:
    """A book in the user's library (a 'reading' in the backend)."""

    reading_id: int | None
    book: Book
    status: str
    date_added: date
    date_read: date | None = None
    rating: int | None = None


@dataclass(frozen=True)
class Review:
    review_id: int
    work_id: str
    author: str
    text: str
    rating: int | None = None
    created: date | None = None
    likes: int = 0
    book_title: str | None = None
    is_mine: bool = False
    author_id: int | None = None  # needed to open the author's public profile
    liked_by_me: bool = False
    reading_id: int | None = None  # the reading the review belongs to (its rating lives there)
    likeable: bool = True  # False when likes cannot be recorded (e.g. fictitious review)


@dataclass(frozen=True)
class Person:
    username: str
    user_id: int | None = None
    bio: str | None = None


@dataclass(frozen=True)
class Profile:
    user_id: int | None
    username: str
    display_name: str
    bio: str | None = None
    member_since: date | None = None
    followers: tuple[Person, ...] = ()
    following: tuple[Person, ...] = ()


@dataclass
class Row:
    """A horizontal shelf on the home page."""

    key: str
    title: str
    books: list[Book] = field(default_factory=list)
    subtitle: str | None = None
