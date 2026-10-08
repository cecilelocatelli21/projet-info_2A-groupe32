import os
from unittest.mock import patch

import psycopg2
import pytest

from business_object.book import Book
from service.book_service import BookService


@pytest.fixture(scope="session", autouse=True)


# def test_get_or_create_by_work_id():
#     """Find a Book based on work_id or create this book"""

#     # GIVEN
#     book = Book(work_id="work id", title="titre", authors="authors of the book", cover_url="http://cover of the book")

#     # WHEN
#     creation_ok = BookDao().create(book)

#     # THEN
#     assert creation_ok
#     assert book.work_id == "work id"
#     assert book.title == "titre"
#     assert book.authors == "authors of the book"
#     assert book.cover_url == "http://cover of the book"
#     assert isinstance(book.book_id, int)


def test_get_book_details_no_work():
    """Fail to get details for a book - the book does not exist in OpenLibrary"""

    # GIVEN
    work_id = "OL11111111111W"
    bookservice = BookService()

    # WHEN / THEN
    assert work_id == "OL11111111111W"
    assert bookservice.get_book_details(work_id) is None

def test_get_book_details_work_ok():
    """Get details for a book with OpenLibrary data"""

    # GIVEN - this is the work_id of the work "Madame Bovary"
    work_id = "OL893707W"
    bookservice = BookService()
    print(work_id)

    # WHEN
    details = bookservice.get_book_details(work_id)

    # THEN
    assert details["work_id"] == "OL893707W"
    assert isinstance(details["book_id"], (int, type(None)))
    assert details["title"] == "Madame Bovary"
    assert details["authors"] == "Flaubert, Gustave"
    assert isinstance(details["cover_url"], str)
    assert isinstance(details["subjects"], list)
    assert isinstance(details["description"], (str, type(None)))
    assert isinstance(details["editions_count"], int)
    assert isinstance(details["editions"], list)
    assert isinstance(details["average_rating"], (float, type(None)))