"""Authentication routes (vertical User).

Endpoints used:
    POST /login    body {username, password} -> {id_user, username, access_token}
    POST /logout   erases the token in the backend (204); needs the Bearer token
"""

from utils.api_client import api_client


def login(username: str, password: str) -> dict:
    """Logs in. On success (200), data is {"id_user", "username", "access_token"}."""
    return api_client.post("/login", json={"username": username, "password": password})


def logout(token: str | None = None) -> dict:
    """Logs out the connected user: the token is erased in the backend (204).

    The token is passed explicitly so that it can still be revoked right before the local session
    is cleared."""
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return api_client.post("/logout", headers=headers, timeout=3)
