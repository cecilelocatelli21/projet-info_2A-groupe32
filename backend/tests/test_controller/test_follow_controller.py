from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from business_object.user import User
from controller import follow_controller
from utils.exceptions import NotFoundError

app = FastAPI()
app.include_router(follow_controller.router)
client = TestClient(app)


def override_service(service):
    app.dependency_overrides[follow_controller.get_follow_service] = lambda: service


def test_get_following_ok_no_sensitive_data():
    """200 with public fields only, in the order given by the service"""

    # GIVEN
    service = MagicMock()
    service.get_following.return_value = [
        User(user_id=5, username="Anne", email="a@mail.fr", password_hash="secret", bio="b"),
        User(user_id=2, username="Cecile", email="c@mail.fr", password_hash="secret", bio=None),
    ]
    override_service(service)

    # WHEN
    response = client.get("/users/1/following")

    # THEN
    assert response.status_code == 200
    assert response.json() == [
        {"user_id": 5, "username": "Anne", "bio": "b"},
        {"user_id": 2, "username": "Cecile", "bio": None},
    ]
    service.get_following.assert_called_once_with(1)


def test_get_following_empty():
    """200 with an empty list"""
    service = MagicMock()
    service.get_following.return_value = []
    override_service(service)

    response = client.get("/users/1/following")

    assert response.status_code == 200
    assert response.json() == []


def test_get_following_not_found():
    """404 when the service raises NotFoundError"""
    service = MagicMock()
    service.get_following.side_effect = NotFoundError("User (id=9999) not found.")
    override_service(service)

    response = client.get("/users/9999/following")

    assert response.status_code == 404


def test_get_followers_ok_no_sensitive_data():
    """200 with public fields only, in the order given by the service"""

    # GIVEN
    service = MagicMock()
    service.get_followers.return_value = [
        User(user_id=3, username="Paul", email="p@mail.fr", password_hash="secret", bio="b"),
    ]
    override_service(service)

    # WHEN
    response = client.get("/users/1/followers")

    # THEN
    assert response.status_code == 200
    assert response.json() == [{"user_id": 3, "username": "Paul", "bio": "b"}]
    service.get_followers.assert_called_once_with(1)
    service.get_following.assert_not_called()


def test_get_followers_empty():
    """200 with an empty list"""
    service = MagicMock()
    service.get_followers.return_value = []
    override_service(service)

    response = client.get("/users/1/followers")

    assert response.status_code == 200
    assert response.json() == []


def test_get_followers_not_found():
    """404 when the service raises NotFoundError"""
    service = MagicMock()
    service.get_followers.side_effect = NotFoundError("User (id=9999) not found.")
    override_service(service)

    response = client.get("/users/9999/followers")

    assert response.status_code == 404
