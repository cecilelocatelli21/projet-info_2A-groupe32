"""User routes (vertical User).

Endpoints used:
    POST /users
    GET /users/me
    GET /users/{user_id}
    GET /users?username=
"""

from utils.api_client import api_client


def create_account(username: str, email: str, password: str) -> dict:
    """Creates an account (201). 409 if the username or the email is already taken."""
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
    """Searches users whose username contains the pattern (list[UserPublicModel])."""
    return api_client.get("/users", params={"username": username})
