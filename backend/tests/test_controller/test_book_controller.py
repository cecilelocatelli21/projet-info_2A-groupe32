from datetime import date
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from business_object.book import Book
from business_object.user import User
from client.openlibrary_client import OpenLibraryClient
from controller import book_controller
from controller.dependencies import get_current_user
from service.book_service import BookService
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
    service.get_book_details.return_value = None #{"error": "notfound", "key": "/works/OL29103511111W"}
    override_service(service)
    app.dependency_overrides[get_current_user] = lambda: User(
        user_id=1, username="test", email="t@mail.fr", password_hash="h", bio=None
    )

    # WHEN
    response = client.get("/OL29103511111W")

    # THEN
    assert response.status_code == 404
    assert response.json() == {'detail': 'The work id has not been found in OpenLibrary.'}
    service.get_book_details.assert_called_once_with("OL29103511111W")


def test_get_book_ok():
    """The result is ok, we get what was expected"""

    # GIVEN
    service = MagicMock()
    service.get_book_details.return_value={
        "work_id": "OL258850W",
        "book_id": 4,
        "title": "Othello",
        "authors": "William Shakespeare",
        "cover_url": "https://ebookzy.com/othello/",
        "subjects": ["Classics", "Shakespeare"],
        "description": "Shakespeare's tragedy of jealousy and suspicion presented scene by scene in comic book format.",
        "editions_count": 0,
        "editions": [],
        "average_rating": 4.3}
    override_service(service)
    app.dependency_overrides[get_current_user] = lambda: User(
        user_id=1, username="test", email="t@mail.fr", password_hash="h", bio=None
    )

    # WHEN
    response = client.get("/OL258850W")
    print(response.status_code, response.text, response.json())
    json = response.json()

    # THEN
    assert response.status_code == 200
    assert json["title"] == "Othello"
    service.get_book_details.assert_called_once_with("OL258850W")


def test_find_by_id_ok():
    """The result is ok, we get what was expected"""

    # GIVEN
    service = MagicMock()
    service.find_by_id.return_value= Book(book_id=3,
                                            work_id= "OL29549062W",
                                            title="À l'ombre des jeunes filles en fleurs",
                                            authors="Marcel Proust",
                                            cover_url="https://covers.openlibrary.org/b/olid/OL10264W-M.jpg")

    override_service(service)
    app.dependency_overrides[get_current_user] = lambda: User(
        user_id=1, username="test", email="t@mail.fr", password_hash="h", bio=None
    )

    # WHEN
    print("coucou1")
    response = client.get("/id/3") #
    print(response.status_code, response.text, response.json())
    json = response.json()
    print("coucou3")

    # THEN
    assert response.status_code == 200
    assert json["book_id"] == 3
    service.find_by_id.assert_called_once_with(3)


def test_find_all_ok():
    """The result is ok, we get what was expected"""
    # J'essaie de reprendre la structure du test "test_get_following_ok_no_sensitive_data" qui fonctionne, mais ici cela ne marche pas, je ne comprends pas pourquoi

    # GIVEN
    service = MagicMock()
    service.find_all.return_value = [
        Book(book_id=1, work_id="OL10263W", title="le petit prince", authors="Antoine de Saint-Exupéry"),
        Book(book_id=2, work_id="OL30053009W", title="Du côté de chez Swann", authors="Marcel Proust"),
    ]
    override_service(service)

    # WHEN
    print("coucou31")
    response = client.get("/find_all/")
    print(response.status_code, response.text)
    print("coucou32")

    # THEN
    assert response.status_code == 200
