"""Authentication routes (vertical User).

Endpoints used:
    POST /login
    POST /logout
"""

from utils.api_client import api_client


def login(username: str, password: str) -> dict:
    """Logs in. On success (200), data is {"access_token": ..., "token_type": "bearer"}."""
    return api_client.post("/login", json={"username": username, "password": password})


def logout() -> dict:
    """Logs out the connected user: the token is erased in the backend (204)."""
    return api_client.post("/logout")
