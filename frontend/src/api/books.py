"""Book routes (vertical Book, and book reviews from vertical Review).

Endpoints used:
    GET /books?q=
    GET /books/{work_id}
    GET /books/{work_id}/reviews
"""

from utils.api_client import api_client


def search_books(query: str) -> dict:
    """Searches books on OpenLibrary (list[BookSearchResultModel]). 503 if unreachable."""
    return api_client.get("/books", params={"q": query})


def get_book(work_id: str) -> dict:
    """Book details (BookDetailModel): description, editions, average rating."""
    return api_client.get(f"/books/{work_id}")


def get_book_reviews(work_id: str) -> dict:
    """Reviews written about a book (list[ReviewReadModel])."""
    return api_client.get(f"/books/{work_id}/reviews")
