"""Authentication routes (vertical User).

Endpoints used:
    POST /login/    (the backend route is declared with a trailing slash)
    POST /logout    (documented in doc/Ex-Libris — Endpoints de l'API.md, NOT implemented in the
                     backend yet: the call is best-effort, see auth.session.logout)
"""

from utils.api_client import api_client


def login(username: str, password: str) -> dict:
    """Logs in. On success (200), data is {"access_token": ..., "token_type": "bearer"}."""
    return api_client.post("/login/", json={"username": username, "password": password})


def logout(token: str) -> dict:
    """Logs out the connected user: the token is erased in the backend (204)."""
    return api_client.post("/logout", headers={"Authorization": f"Bearer {token}"}, timeout=2)
