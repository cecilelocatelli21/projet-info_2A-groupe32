from unittest.mock import MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from business_object.user import User
from controller import login_controller, user_controller
from controller.dependencies import get_current_user
from utils.exceptions import ConflictError, ForbiddenError, NotFoundError

app = FastAPI()
app.include_router(login_controller.router)
app.include_router(user_controller.router)
client = TestClient(app)


def anne():
    """The logged-in user of most tests (user_id 1). A new object for each test."""
    return User(
        user_id=1,
        username="anne",
        email="anne@mail.fr",
        password_hash="hash-secret",
        bio="bio",
        access_token="token-anne",
    )


def cecile():
    """Another user (user_id 2), whose email must never be shown to Anne."""
    return User(
        user_id=2,
        username="cecile",
        email="cecile@mail.fr",
        password_hash="hash-secret",
        bio=None,
        access_token=None,
    )


def setup(service, current_user=None):
    """Replaces the service by a mock and, if given, logs current_user in.

    The overrides are cleared first, so that no test depends on the previous one.
    Without current_user, the real get_current_user runs and reads the token.
    """
    app.dependency_overrides.clear()
    app.dependency_overrides[user_controller.get_user_service] = lambda: service
    app.dependency_overrides[login_controller.get_user_service] = lambda: service
    if current_user is not None:
        app.dependency_overrides[get_current_user] = lambda: current_user


# ---------- Authentication: get_current_user (no override) ----------
# The UserService used by get_current_user is replaced with patch(...), which is
# undone at the end of the "with" block. Replacing UserDao().find_by_token
# directly would stay in place for the DAO tests, which run afterwards.


def test_route_without_token_401():
    """401 when the Authorization header is missing"""

    # GIVEN
    setup(MagicMock())

    # WHEN
    response = client.get("/users/me")

    # THEN
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_route_with_unknown_token_401():
    """401 when no user owns the token"""

    # GIVEN
    setup(MagicMock())

    with patch("controller.dependencies.UserService") as service_class:
        service_class.return_value.find_by_token.return_value = None

        # WHEN
        response = client.get("/users/me", headers={"Authorization": "Bearer faux-jeton"})

    # THEN
    assert response.status_code == 401
    service_class.return_value.find_by_token.assert_called_once_with("faux-jeton")


def test_route_with_wrong_scheme_401():
    """401 when the header does not use the Bearer scheme"""

    # GIVEN
    setup(MagicMock())

    with patch("controller.dependencies.UserService") as service_class:
        service_class.return_value.find_by_token.return_value = anne()

        # WHEN
        response = client.get("/users/me", headers={"Authorization": "Basic token-anne"})

    # THEN
    assert response.status_code == 401
    service_class.return_value.find_by_token.assert_not_called()


def test_route_with_valid_token_200():
    """The token of the Authorization header identifies the user"""

    # GIVEN
    setup(MagicMock())

    with patch("controller.dependencies.UserService") as service_class:
        service_class.return_value.find_by_token.return_value = anne()

        # WHEN
        response = client.get("/users/me", headers={"Authorization": "Bearer token-anne"})

    # THEN
    assert response.status_code == 200
    assert response.json()["username"] == "anne"
    service_class.return_value.find_by_token.assert_called_once_with("token-anne")


# ---------- POST /users (without token) ----------


def test_create_user_201():
    """201 with the private view of the new account, no token needed"""

    # GIVEN
    service = MagicMock()
    service.create_account.return_value = anne()
    setup(service)

    # WHEN
    response = client.post(
        "/users", json={"username": "anne", "email": "anne@mail.fr", "password": "motdepasse"}
    )

    # THEN
    assert response.status_code == 201
    assert response.json() == {
        "user_id": 1,
        "username": "anne",
        "bio": "bio",
        "email": "anne@mail.fr",
    }
    service.create_account.assert_called_once_with(
        username="anne", email="anne@mail.fr", password="motdepasse"
    )


def test_create_user_409():
    """409 when the username or the email is already used"""

    # GIVEN
    service = MagicMock()
    service.create_account.side_effect = ConflictError("Username 'anne' is already taken.")
    setup(service)

    # WHEN
    response = client.post(
        "/users", json={"username": "anne", "email": "anne@mail.fr", "password": "motdepasse"}
    )

    # THEN
    assert response.status_code == 409
    assert response.json() == {"detail": "Username 'anne' is already taken."}


def test_create_user_fail_500():
    """500 when the service could not create the account (returns None)"""

    # GIVEN
    service = MagicMock()
    service.create_account.return_value = None
    setup(service)

    # WHEN
    response = client.post(
        "/users", json={"username": "anne", "email": "anne@mail.fr", "password": "motdepasse"}
    )

    # THEN
    assert response.status_code == 500


def test_create_user_password_too_short_422():
    """422 when the password is too short: Pydantic refuses it before the service"""

    # GIVEN
    service = MagicMock()
    setup(service)

    # WHEN
    response = client.post(
        "/users", json={"username": "anne", "email": "anne@mail.fr", "password": "1"}
    )

    # THEN
    assert response.status_code == 422
    service.create_account.assert_not_called()


def test_create_user_invalid_email_422():
    """422 when the email is not valid"""

    # GIVEN
    service = MagicMock()
    setup(service)

    # WHEN
    response = client.post(
        "/users", json={"username": "anne", "email": "pas-un-email", "password": "motdepasse"}
    )

    # THEN
    assert response.status_code == 422
    service.create_account.assert_not_called()


def test_create_user_username_too_long_422():
    """422 when the username is longer than 30 characters (VARCHAR(30))"""

    # GIVEN
    service = MagicMock()
    setup(service)

    # WHEN
    response = client.post(
        "/users", json={"username": "a" * 31, "email": "anne@mail.fr", "password": "motdepasse"}
    )

    # THEN
    assert response.status_code == 422
    service.create_account.assert_not_called()


def test_create_user_username_with_spaces_422():
    """422 when the username starts or ends with a space"""

    # GIVEN
    service = MagicMock()
    setup(service)

    # WHEN
    response = client.post(
        "/users", json={"username": " anne", "email": "anne@mail.fr", "password": "motdepasse"}
    )

    # THEN
    assert response.status_code == 422
    service.create_account.assert_not_called()


def test_create_user_missing_field_422():
    """422 when a required field is missing"""

    # GIVEN
    service = MagicMock()
    setup(service)

    # WHEN
    response = client.post("/users", json={"username": "anne", "password": "motdepasse"})

    # THEN
    assert response.status_code == 422
    service.create_account.assert_not_called()


# ---------- POST /login, POST /logout ----------


def test_login_200():
    """200 with the user_id, the username and the token"""

    # GIVEN
    service = MagicMock()
    service.login.return_value = anne()
    setup(service)

    # WHEN
    response = client.post("/login", json={"username": "anne", "password": "motdepasse"})

    # THEN
    assert response.status_code == 200
    assert response.json() == {"id_user": 1, "username": "anne", "access_token": "token-anne"}
    service.login.assert_called_once_with("anne", "motdepasse")


def test_login_401():
    """401 when the username or the password is wrong"""

    # GIVEN
    service = MagicMock()
    service.login.return_value = None
    setup(service)

    # WHEN
    response = client.post("/login", json={"username": "anne", "password": "mauvais"})

    # THEN
    assert response.status_code == 401


def test_login_missing_password_422():
    """422 when the password is missing"""

    # GIVEN
    service = MagicMock()
    setup(service)

    # WHEN
    response = client.post("/login", json={"username": "anne"})

    # THEN
    assert response.status_code == 422
    service.login.assert_not_called()


def test_logout_204():
    """204 and the token of the logged-in user is removed"""

    # GIVEN
    service = MagicMock()
    current_user = anne()
    setup(service, current_user)

    # WHEN
    response = client.post("/logout")

    # THEN
    assert response.status_code == 204
    service.logout.assert_called_once_with(current_user)


def test_logout_without_token_401():
    """401 when logging out without a token"""

    # GIVEN
    service = MagicMock()
    setup(service)

    # WHEN
    response = client.post("/logout")

    # THEN
    assert response.status_code == 401
    service.logout.assert_not_called()


# ---------- GET /users/me ----------


def test_read_me_200_with_email():
    """200 with the private view: the user sees their own email"""

    # GIVEN
    setup(MagicMock(), anne())

    # WHEN
    response = client.get("/users/me")

    # THEN
    assert response.status_code == 200
    assert response.json() == {
        "user_id": 1,
        "username": "anne",
        "bio": "bio",
        "email": "anne@mail.fr",
    }


def test_read_me_never_shows_secrets():
    """The response never contains the password hash nor the token"""

    # GIVEN
    setup(MagicMock(), anne())

    # WHEN
    body = client.get("/users/me").json()

    # THEN
    assert "password_hash" not in body
    assert "access_token" not in body


# ---------- GET /users/all ----------


def test_find_all_users_200_without_emails():
    """200 with the public view of every user"""

    # GIVEN
    service = MagicMock()
    service.find_all.return_value = [anne(), cecile()]
    setup(service, anne())

    # WHEN
    response = client.get("/users/all")

    # THEN
    assert response.status_code == 200
    assert response.json() == [
        {"user_id": 1, "username": "anne", "bio": "bio"},
        {"user_id": 2, "username": "cecile", "bio": None},
    ]


def test_find_all_users_without_token_401():
    """401 when listing users without a token"""

    # GIVEN
    setup(MagicMock())

    # WHEN
    response = client.get("/users/all")

    # THEN
    assert response.status_code == 401


# ---------- GET /users?username= ----------


def test_search_users_200_without_emails():
    """200 with the public view of the users found"""

    # GIVEN
    service = MagicMock()
    service.search.return_value = [cecile()]
    setup(service, anne())

    # WHEN
    response = client.get("/users", params={"username": "ce"})

    # THEN
    assert response.status_code == 200
    assert response.json() == [{"user_id": 2, "username": "cecile", "bio": None}]
    service.search.assert_called_once_with("ce")


def test_search_users_no_parameter():
    """Without ?username=, the service receives an empty pattern"""

    # GIVEN
    service = MagicMock()
    service.search.return_value = []
    setup(service, anne())

    # WHEN
    response = client.get("/users")

    # THEN
    assert response.status_code == 200
    assert response.json() == []
    service.search.assert_called_once_with("")


def test_search_users_without_token_401():
    """401 when searching without a token"""

    # GIVEN
    service = MagicMock()
    setup(service)

    # WHEN
    response = client.get("/users", params={"username": "ce"})

    # THEN
    assert response.status_code == 401
    service.search.assert_not_called()


# ---------- GET /users/{user_id} ----------


def test_user_by_id_200_without_email():
    """200 with the public view: another user's email is never shown"""

    # GIVEN
    service = MagicMock()
    service.find_by_id.return_value = cecile()
    setup(service, anne())

    # WHEN
    response = client.get("/users/2")

    # THEN
    assert response.status_code == 200
    assert response.json() == {"user_id": 2, "username": "cecile", "bio": None}
    service.find_by_id.assert_called_once_with(2)


def test_user_by_id_404():
    """404 when the user does not exist"""

    # GIVEN
    service = MagicMock()
    service.find_by_id.return_value = None
    setup(service, anne())

    # WHEN
    response = client.get("/users/999")

    # THEN
    assert response.status_code == 404
    assert response.json() == {"detail": "User (id=999) not found."}


def test_user_by_id_not_an_integer_422():
    """422 when the user_id is not an integer"""

    # GIVEN
    service = MagicMock()
    setup(service, anne())

    # WHEN
    response = client.get("/users/abc")

    # THEN
    assert response.status_code == 422
    service.find_by_id.assert_not_called()


def test_user_by_id_without_token_401():
    """401 when reading a profile without a token"""

    # GIVEN
    service = MagicMock()
    setup(service)

    # WHEN
    response = client.get("/users/2")

    # THEN
    assert response.status_code == 401
    service.find_by_id.assert_not_called()


# ---------- PUT /users/{user_id} ----------


def test_update_user_200():
    """200 with the updated account; only the fields sent are passed on"""

    # GIVEN
    service = MagicMock()
    current_user = anne()
    updated = anne()
    updated.bio = "nouvelle bio"
    service.update_profile.return_value = updated
    setup(service, current_user)

    # WHEN
    response = client.put("/users/1", json={"bio": "nouvelle bio"})

    # THEN
    assert response.status_code == 200
    assert response.json()["bio"] == "nouvelle bio"
    service.update_profile.assert_called_once_with(current_user, 1, bio="nouvelle bio", email=None)


def test_update_user_403():
    """403 when modifying someone else's account"""

    # GIVEN
    service = MagicMock()
    service.update_profile.side_effect = ForbiddenError("You can only modify your own account.")
    setup(service, anne())

    # WHEN
    response = client.put("/users/2", json={"bio": "piratage"})

    # THEN
    assert response.status_code == 403


def test_update_user_404():
    """404 when the account does not exist"""

    # GIVEN
    service = MagicMock()
    service.update_profile.side_effect = NotFoundError("User 999 not found.")
    setup(service, anne())

    # WHEN
    response = client.put("/users/999", json={"bio": "x"})

    # THEN
    assert response.status_code == 404


def test_update_user_409():
    """409 when the new email is already used by another account"""

    # GIVEN
    service = MagicMock()
    service.update_profile.side_effect = ConflictError("Email 'cecile@mail.fr' is already used.")
    setup(service, anne())

    # WHEN
    response = client.put("/users/1", json={"email": "cecile@mail.fr"})

    # THEN
    assert response.status_code == 409


def test_update_user_fail_500():
    """500 when the service could not save the changes (returns None)"""

    # GIVEN
    service = MagicMock()
    service.update_profile.return_value = None
    setup(service, anne())

    # WHEN
    response = client.put("/users/1", json={"bio": "x"})

    # THEN
    assert response.status_code == 500


def test_update_user_invalid_email_422():
    """422 when the new email is not valid"""

    # GIVEN
    service = MagicMock()
    setup(service, anne())

    # WHEN
    response = client.put("/users/1", json={"email": "pas-un-email"})

    # THEN
    assert response.status_code == 422
    service.update_profile.assert_not_called()


def test_update_user_bio_too_long_422():
    """422 when the bio is longer than 1000 characters"""

    # GIVEN
    service = MagicMock()
    setup(service, anne())

    # WHEN
    response = client.put("/users/1", json={"bio": "a" * 1001})

    # THEN
    assert response.status_code == 422
    service.update_profile.assert_not_called()


def test_update_user_without_token_401():
    """401 when modifying an account without a token"""

    # GIVEN
    service = MagicMock()
    setup(service)

    # WHEN
    response = client.put("/users/1", json={"bio": "x"})

    # THEN
    assert response.status_code == 401
    service.update_profile.assert_not_called()


# ---------- PUT /users/{user_id}/password ----------


def test_change_password_204():
    """204 and the passwords are passed to the service"""

    # GIVEN
    service = MagicMock()
    current_user = anne()
    setup(service, current_user)

    # WHEN
    response = client.put(
        "/users/1/password",
        json={"old_password": "motdepasse", "new_password": "nouveaumotdepasse"},
    )

    # THEN
    assert response.status_code == 204
    service.change_password.assert_called_once_with(
        current_user, 1, "motdepasse", "nouveaumotdepasse"
    )


def test_change_password_wrong_old_password_400():
    """400 when the old password is wrong"""

    # GIVEN
    service = MagicMock()
    service.change_password.side_effect = ValueError("Old password is incorrect.")
    setup(service, anne())

    # WHEN
    response = client.put(
        "/users/1/password",
        json={"old_password": "mauvais", "new_password": "nouveaumotdepasse"},
    )

    # THEN
    assert response.status_code == 400


def test_change_password_403():
    """403 when changing someone else's password"""

    # GIVEN
    service = MagicMock()
    service.change_password.side_effect = ForbiddenError("You can only modify your own account.")
    setup(service, anne())

    # WHEN
    response = client.put(
        "/users/2/password",
        json={"old_password": "motdepasse", "new_password": "nouveaumotdepasse"},
    )

    # THEN
    assert response.status_code == 403


def test_change_password_404():
    """404 when the account does not exist"""

    # GIVEN
    service = MagicMock()
    service.change_password.side_effect = NotFoundError("User 999 not found.")
    setup(service, anne())

    # WHEN
    response = client.put(
        "/users/999/password",
        json={"old_password": "motdepasse", "new_password": "nouveaumotdepasse"},
    )

    # THEN
    assert response.status_code == 404


def test_change_password_new_password_too_short_422():
    """422 when the new password is too short"""

    # GIVEN
    service = MagicMock()
    setup(service, anne())

    # WHEN
    response = client.put(
        "/users/1/password", json={"old_password": "motdepasse", "new_password": "1"}
    )

    # THEN
    assert response.status_code == 422
    service.change_password.assert_not_called()


def test_change_password_without_token_401():
    """401 when changing a password without a token"""

    # GIVEN
    service = MagicMock()
    setup(service)

    # WHEN
    response = client.put(
        "/users/1/password",
        json={"old_password": "motdepasse", "new_password": "nouveaumotdepasse"},
    )

    # THEN
    assert response.status_code == 401
    service.change_password.assert_not_called()


# ---------- DELETE /users/{user_id} ----------


def test_delete_user_204():
    """204 and the account of the logged-in user is deleted"""

    # GIVEN
    service = MagicMock()
    current_user = anne()
    setup(service, current_user)

    # WHEN
    response = client.delete("/users/1")

    # THEN
    assert response.status_code == 204
    service.delete_account.assert_called_once_with(current_user, 1)


def test_delete_user_403():
    """403 when deleting someone else's account"""

    # GIVEN
    service = MagicMock()
    service.delete_account.side_effect = ForbiddenError("You can only modify your own account.")
    setup(service, anne())

    # WHEN
    response = client.delete("/users/2")

    # THEN
    assert response.status_code == 403


def test_delete_user_404():
    """404 when the account does not exist"""

    # GIVEN
    service = MagicMock()
    service.delete_account.side_effect = NotFoundError("User 999 not found.")
    setup(service, anne())

    # WHEN
    response = client.delete("/users/999")

    # THEN
    assert response.status_code == 404


def test_delete_user_without_token_401():
    """401 when deleting an account without a token"""

    # GIVEN
    service = MagicMock()
    setup(service)

    # WHEN
    response = client.delete("/users/1")

    # THEN
    assert response.status_code == 401
    service.delete_account.assert_not_called()