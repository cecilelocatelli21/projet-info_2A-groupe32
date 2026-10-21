"""Local search / filter / sort over a list of books.

Used for the demo catalogue and as a fallback whenever the backend has no search route yet
(``GET /books/search`` is still commented out in book_controller.py).
"""

from __future__ import annotations

import unicodedata
from collections.abc import Iterable

from data.models import Book

SORT_LABELS = {
    "relevance": "Relevance",
    "rating": "Top rated",
    "recent": "Most recent",
    "title": "Title (A → Z)",
    "author": "Author (A → Z)",
}


def normalize(text: str | None) -> str:
    """Lower-case and strip accents so that 'etranger' matches 'L'Étranger'."""
    if not text:
        return ""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).lower().strip()


def _score(book: Book, query: str) -> float:
    title = normalize(book.title)
    authors = normalize(book.authors_label)
    score = 0.0
    if title.startswith(query):
        score += 3
    elif query in title:
        score += 2
    if query in authors:
        score += 1.5
    if any(query in normalize(g) for g in book.genres):
        score += 1
    if query in normalize(book.description):
        score += 0.5
    return score


def filter_books(
    books: Iterable[Book],
    query: str = "",
    genres: Iterable[str] = (),
    authors: Iterable[str] = (),
    sort: str = "relevance",
) -> list[Book]:
    """Filter by text, genres and authors, then sort."""
    genres = set(genres)
    authors = set(authors)
    q = normalize(query)

    result = []
    for book in books:
        if genres and not genres.intersection(book.genres):
            continue
        if authors and not authors.intersection(book.authors):
            continue
        if q and _score(book, q) == 0:
            continue
        result.append(book)

    if sort == "title":
        result.sort(key=lambda b: normalize(b.title))
    elif sort == "author":
        result.sort(key=lambda b: (normalize(b.authors_label), normalize(b.title)))
    elif sort == "recent":
        result.sort(key=lambda b: (-(b.published or 0), normalize(b.title)))
    elif sort == "rating":
        result.sort(key=lambda b: (-(b.rating or 0), -b.ratings_count, normalize(b.title)))
    elif q:  # relevance with a query
        result.sort(key=lambda b: (-_score(b, q), -(b.rating or 0), normalize(b.title)))
    else:  # relevance without a query: most popular first
        result.sort(key=lambda b: (-b.ratings_count, normalize(b.title)))
    return result
