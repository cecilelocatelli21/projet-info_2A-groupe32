"""Session handling. The demo login is isolated here so it can be removed in one place.

To switch to real authentication only: set ``EXLIBRIS_ENABLE_DEMO_LOGIN=false``. The demo mode
then disappears from the login page; ``api_login`` (real POST /login) stays.
"""

from __future__ import annotations

import streamlit as st

from data import demo_catalog
from utils.api_client import api_client

_KEYS = (
    "mode", "user_id", "username", "display_name", "access_token", "token_verified",
    "player", "_repo_demo", "_liked_reviews",
)


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


def _verify_token(user_id, token: str) -> bool | None:
    """Confirms that the token opens a protected route (GET /users/{id}/reviews needs a Bearer token).

    True = accepted, False = refused (401), None = inconclusive (server error, route unavailable)."""
    response = api_client.get(f"/users/{user_id}/reviews", headers={"Authorization": f"Bearer {token}"})
    status = response["status_code"]
    if status == 200:
        return True
    return False if status == 401 else None


def api_login(username: str, password: str) -> str | None:
    """Real login: ``POST /login/`` with the JSON body {username, password}.

    The backend answers {"id_user", "username", "access_token"}. The password is only used for this
    call: it is neither stored nor logged. Returns an error message, or None on success."""
    response = api_client.post("/login/", json={"username": username, "password": password})
    status, data = response["status_code"], response["data"]
    if status == 200 and isinstance(data, dict) and data.get("access_token"):
        user_id = data.get("user_id", data.get("id_user", data.get("id_player")))
        verified = _verify_token(user_id, data["access_token"])
        if verified is False:
            return "Connexion refusée : le serveur n'a pas reconnu le jeton reçu."
        logout()  # never keep anything from a previous (real or demo) session
        st.session_state.update(
            mode="api",
            user_id=user_id,
            username=data.get("username", username),
            display_name=data.get("username", username),
            access_token=data["access_token"],
            token_verified=verified,
        )
        return None
    if status == 200:
        return "Réponse inattendue du serveur (pas de jeton reçu)."
    if status in (401, 404):
        return "Pseudo ou mot de passe incorrect."
    if status == 422:
        return "Renseigne un pseudo et un mot de passe valides."
    if status == 0:
        return "Le serveur est injoignable pour le moment. Réessaie dans un instant."
    return "Erreur du serveur, réessaie plus tard."


def status_label() -> str:
    """Discreet indicator for the user menu."""
    if is_demo():
        return f"Mode démonstration — {display_name()}"
    return f"Connecté — {display_name()}"


def expire(message: str = "Ta session a expiré, reconnecte-toi.") -> None:
    """The backend refused the token: back to the login page with an explanation."""
    logout()
    st.session_state["login_notice"] = message


def logout() -> None:
    for key in _KEYS:
        st.session_state.pop(key, None)
    st.session_state.pop("demo_state", None)
