"""User routes (vertical User). Only routes that exist in backend/src/controller/user_controller.py.

Endpoints used:
    POST /users                     create an account (no token needed)
    GET /users/me                   own profile, with the email (logged in)
    GET /users?username=            search users, case-insensitive "contains" (logged in)
    GET /users/{user_id}            public profile (logged in)
    PUT /users/{user_id}            change bio and/or email, owner only; a field left out is unchanged
    PUT /users/{user_id}/password   change password, owner only (204)
    DELETE /users/{user_id}         delete one's own account, owner only (204)

Note: ``/player/{id_player}`` (PUT / DELETE) is NOT used: it acts on the former template ``player``
table (elo, pokemon_fan, no bio, no authentication), not on Ex-Libris accounts.
"""

from utils.api_client import api_client


def create_account(username: str, email: str, password: str) -> dict:
    """Creates an account (201). 409 if the username or the email is already taken.

    Body (UserModel): {"username", "email", "password"}. Answer (UserReadModel): user_id, username,
    bio, email. No token is returned: the user must log in afterwards."""
    return api_client.post(
        "/users", json={"username": username, "email": email, "password": password}
    )


def get_me() -> dict:
    """Own profile, with the email (UserReadModel)."""
    return api_client.get("/users/me")


def get_user(user_id: int) -> dict:
    """Public profile of a user (UserPublicModel): user_id, username, bio. 404 if unknown."""
    return api_client.get(f"/users/{user_id}")


def search_users(username: str) -> dict:
    """Users whose username contains the text, sorted by username (list[UserPublicModel])."""
    return api_client.get("/users", params={"username": username})


def update_profile(user_id: int, bio: str | None = None, email: str | None = None) -> dict:
    """Updates the bio and/or the email (UserUpdateModel). Only the given fields are sent: the
    backend leaves a missing field unchanged. 403 not the owner, 404 unknown, 409 email taken."""
    body = {k: v for k, v in (("bio", bio), ("email", email)) if v is not None}
    return api_client.put(f"/users/{user_id}", json=body)


def change_password(user_id: int, old_password: str, new_password: str) -> dict:
    """Changes the password (PasswordChangeModel). 204 on success, 400 wrong old password."""
    return api_client.put(
        f"/users/{user_id}/password",
        json={"old_password": old_password, "new_password": new_password},
    )


def delete_account(user_id: int) -> dict:
    """Deletes one's own account (204). 403 if user_id is not the token owner's, 404 unknown."""
    return api_client.delete(f"/users/{user_id}")
