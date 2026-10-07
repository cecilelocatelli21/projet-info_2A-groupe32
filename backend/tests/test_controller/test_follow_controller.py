from datetime import date
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from business_object.follow import Follow
from business_object.user import User
from controller import follow_controller
from controller.dependencies import get_current_user
from utils.exceptions import ConflictError, NotFoundError

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


# ---------------------------------------------------------------- POST follow

connected_user = User(user_id=1, username="Moussa", email="m@mail.fr", password_hash="secret")


def login_as(user):
    """Simulate a valid token: get_current_user returns the given user"""
    app.dependency_overrides[get_current_user] = lambda: user


def test_follow_created():
    """201 with the created subscription; the follower is the connected user"""

    # GIVEN
    login_as(connected_user)
    followed = User(user_id=2, username="Cecile", email="c@mail.fr", password_hash="secret")
    service = MagicMock()
    service.follow.return_value = Follow(connected_user, followed, date(2026, 10, 7))
    override_service(service)

    # WHEN
    response = client.post("/users/2/follow")

    # THEN
    assert response.status_code == 201
    assert response.json() == {"follower_id": 1, "followed_id": 2, "follow_date": "2026-10-07"}
    service.follow.assert_called_once_with(user=connected_user, followed_id=2)


def test_follow_not_found():
    """404 when the service raises NotFoundError"""
    login_as(connected_user)
    service = MagicMock()
    service.follow.side_effect = NotFoundError("User (id=9999) not found.")
    override_service(service)

    response = client.post("/users/9999/follow")

    assert response.status_code == 404


def test_follow_himself():
    """400 when the service raises ValueError"""
    login_as(connected_user)
    service = MagicMock()
    service.follow.side_effect = ValueError("A user cannot follow himself.")
    override_service(service)

    response = client.post("/users/1/follow")

    assert response.status_code == 400


def test_follow_conflict():
    """409 when the subscription already exists"""
    login_as(connected_user)
    service = MagicMock()
    service.follow.side_effect = ConflictError("already follows")
    override_service(service)

    response = client.post("/users/2/follow")

    assert response.status_code == 409


def test_follow_requires_token():
    """401 without token: the service is never called"""
    app.dependency_overrides.pop(get_current_user, None)
    service = MagicMock()
    override_service(service)

    response = client.post("/users/2/follow")

    assert response.status_code == 401
    service.follow.assert_not_called()


# ---------------------------------------------------------------- DELETE follow


def test_unfollow_ok():
    """204 without content; the follower is the connected user"""

    # GIVEN
    login_as(connected_user)
    service = MagicMock()
    service.unfollow.return_value = True
    override_service(service)

    # WHEN
    response = client.delete("/users/2/follow")

    # THEN
    assert response.status_code == 204
    assert response.content == b""
    service.unfollow.assert_called_once_with(user=connected_user, followed_id=2)


def test_unfollow_not_following():
    """404 when the service raises NotFoundError"""
    login_as(connected_user)
    service = MagicMock()
    service.unfollow.side_effect = NotFoundError("User (id=1) does not follow user (id=2).")
    override_service(service)

    response = client.delete("/users/2/follow")

    assert response.status_code == 404


def test_unfollow_requires_token():
    """401 without token: the service is never called"""
    app.dependency_overrides.pop(get_current_user, None)
    service = MagicMock()
    override_service(service)

    response = client.delete("/users/2/follow")

    assert response.status_code == 401
    service.unfollow.assert_not_called()
