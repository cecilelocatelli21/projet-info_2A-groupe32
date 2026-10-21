from datetime import date
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from business_object.book import Book
from business_object.user import User
from controller import book_controller
from controller.dependencies import get_current_user
from utils.exceptions import ConflictError, NotFoundError

app = FastAPI()
app.include_router(book_controller.router)
client = TestClient(app)


def override_service(service):
    app.dependency_overrides[book_controller.get_book_service] = lambda: service


def test_get_book_work_id_not_found():
    """The work_id is not found in OpenLibrary when the method get_book is called"""

    # GIVEN
    service = MagicMock()
    service.get_book_details.return_value = {
        "error": "notfound",
        "key": "/works/OL29103511111W"
        }
    override_service(service)

    # WHEN
    response = client.get("/books/OL29103511111W")

    # THEN
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
    # service.get_book_details.assert_called_once_with(1)


def test_get_book_ok():
    """The result is ok, we get what was expected"""

    # GIVEN
    openlibraryclient = MagicMock()
    openlibraryclient._get.return_value = {
        "lc_classifications": ["PR2829.A3 L533 1908"],
        "description": "Shakespeare's tragedy of jealousy and suspicion presented scene by scene in comic book format.",
        "title": "Othello",
        "covers": [7165018, 5249002],
        "first_sentence": {"type": "/type/text", "value": "RODERIGO Tush, never tell me!"},
        "subject_places": ["Venice (Italy)", "Cyprus"],
        "first_publish_date": "August 7, 2006",
        "subject_people": [
            "William Shakespeare (1564-1616)",
            "Othello (Fictitious character from Shakespeare)",
        ],
        "location": "/works/OL258850W",
        "key": "/works/OL258850W",
        "authors": [{"author": {"key": "/authors/OL9388A"}, "type": {"key": "/type/author_role"}}],
        "excerpts": [
            {"excerpt": "RODERIGO Tush, never tell me!"},
            {
                "excerpt": "Roderigo and lago rouse Brabantio from his bed to tell him of Desdemona's rebellion."
            },
        ],
        "subjects": ["Classics", "Shakespeare"],
        "type": {"key": "/type/work"},
        "subject_times": ["16th century"],
        "links": [
            {
                "title": "Othello-Ebookzy",
                "url": "https://ebookzy.com/othello/",
                "type": {"key": "/type/link"},
            },
            {
                "title": "Amazon.com",
                "url": "https://www.amazon.com/Othello-Hardcover-Library-William-Shakespeare/dp/9354992099/ref=sr_1_1?crid=1Q5D4KWPQ9UE4&dib=eyJ2IjoiMSJ9.KRteP4yVHuOKnzgkOqgXTU6VOkUshyflhEQSV6hdpSU.clQZtduPuKkQAAH19ONZHyN6WhHhz0WHmQtxlDowNgY&dib_tag=se&keywords=9354992099&nsdOptOutParam=true&qid=1777888800&s=books&sprefix=9354992099%2Cstripbooks-intl-ship%2C342&sr=1-1",
                "type": {"key": "/type/link"},
            },
            {
                "title": "Online Books Page",
                "url": "https://onlinebooks.library.upenn.edu/webbin/gutbook/lookup?num=7185",
                "type": {"key": "/type/link"},
            },
        ],
        "genres": ["/tags/OL167T", "/tags/OL174T"],
        "latest_revision": 75,
        "revision": 75,
        "created": {"type": "/type/datetime", "value": "2009-10-24T02:04:29.654597"},
        "last_modified": {"type": "/type/datetime", "value": "2026-09-24T05:52:05.186926"},
    }
    override_service(openlibraryclient)

    # WHEN
    response = client.get("/books/OL258850W")

    # THEN
    assert response.status_code == 200
    # service.get_book_details.assert_called_once_with(1)
