"""User routes (vertical User).

Endpoints used:
    POST /user/users   (the user router is mounted under the "/user" prefix in backend/src/main.py;
                        the documented path /users is tried as a fallback if that prefix is removed)
    GET /users/me
    GET /users/{user_id}
    GET /users?username=
"""

from utils.api_client import api_client

CREATE_ACCOUNT_PATHS = ("/user/users", "/users")


def create_account(username: str, email: str, password: str) -> dict:
    """Creates an account (201). 409 if the username or the email is already taken.

    Body (UserModel): {"username", "email", "password"}. Answer (UserReadModel): user_id, username,
    bio, email. No token is returned: the user must log in afterwards."""
    payload = {"username": username, "email": email, "password": password}
    for path in CREATE_ACCOUNT_PATHS:
        response = api_client.post(path, json=payload)
        if response["status_code"] != 404:  # 404 = route not mounted under this path
            break
    return response


def get_me() -> dict:
    """Own profile, with the email (UserReadModel)."""
    return api_client.get("/users/me")


def get_user(user_id: int) -> dict:
    """Public profile of a user (UserPublicModel): user_id, username, bio. 404 if unknown."""
    return api_client.get(f"/users/{user_id}")


def search_users(username: str) -> dict:
    """Searches users whose username contains the pattern (list[UserPublicModel])."""
    return api_client.get("/users", params={"username": username})
