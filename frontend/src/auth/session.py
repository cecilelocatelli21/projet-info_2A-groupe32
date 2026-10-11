"""Session handling. The demo login is isolated here so it can be removed in one place.

To switch to real authentication only: set ``EXLIBRIS_ENABLE_DEMO_LOGIN=false``. The demo mode
then disappears from the login page; ``api_login`` (real POST /login) stays.
"""

from __future__ import annotations

import streamlit as st

from data import demo_catalog
from utils.api_client import api_client

_KEYS = ("mode", "user_id", "username", "display_name", "access_token", "player", "_repo_demo")


def is_logged_in() -> bool:
    return st.session_state.get("mode") in {"demo", "api"}


def is_demo() -> bool:
    return st.session_state.get("mode") == "demo"


def display_name() -> str:
    return st.session_state.get("display_name") or "Lecteur"


def demo_login() -> None:
    """Fictitious user, no token, no password, no call to the backend."""
    logout()
    st.session_state.update(
        mode="demo",
        user_id=demo_catalog.DEMO_USER_ID,
        username=demo_catalog.DEMO_USERNAME,
        display_name=demo_catalog.DEMO_DISPLAY_NAME,
    )


def api_login(username: str, password: str) -> str | None:
    """Real login through the backend. Returns an error message, or None on success."""
    response = api_client.post("/login/", json={"username": username, "password": password})
    status, data = response["status_code"], response["data"]
    if status == 200 and isinstance(data, dict):
        logout()
        st.session_state.update(
            mode="api",
            user_id=data.get("user_id", data.get("id_player")),
            username=data.get("username", username),
            display_name=data.get("username", username),
            access_token=data.get("access_token"),
        )
        return None
    if status == 401:
        return "Identifiants invalides."
    if status == 0:
        return "Le serveur est injoignable pour le moment."
    return "Erreur du serveur, réessaie plus tard."


def logout() -> None:
    for key in _KEYS:
        st.session_state.pop(key, None)
    st.session_state.pop("demo_state", None)
