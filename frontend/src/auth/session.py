"""Session handling: real login / signup / logout, plus the demo login isolated so it can be removed.

To switch to real authentication only: set ``EXLIBRIS_ENABLE_DEMO_LOGIN=false``. The demo mode
then disappears from the login page; ``api_login`` (real POST /login/) stays.
"""

from __future__ import annotations

import streamlit as st

from api import auth
from api.users import create_account
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
    return st.session_state.get("display_name") or "Reader"


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
    """Confirms that the token opens a protected route (GET /user/users/{id} needs a Bearer token).

    True = accepted, False = refused (401), None = inconclusive (server error, route unavailable)."""
    response = api_client.get(f"/user/users/{user_id}", headers={"Authorization": f"Bearer {token}"})
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
            return "Login failed: the server did not accept the session token it issued."
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
        return "Unexpected server response (no session token received)."
    if status in (401, 404):
        return "Incorrect username or password."
    if status == 422:
        return "Please enter a valid username and password."
    if status == 0:
        return "The server is unreachable right now. Please try again in a moment."
    return "Something went wrong on the server. Please try again later."


def _validation_message(detail) -> str:
    """Turns a FastAPI/Pydantic 422 ``detail`` list into one readable sentence."""
    fields = {"username": "Username", "email": "Email", "password": "Password"}
    messages = []
    if isinstance(detail, list):
        for item in detail:
            loc = item.get("loc", []) if isinstance(item, dict) else []
            field = next((fields[x] for x in loc if x in fields), None)
            kind = item.get("type", "") if isinstance(item, dict) else ""
            if field == "Email":
                messages.append("Please enter a valid email address.")
            elif field and "too_short" in kind:
                messages.append(f"{field} is too short.")
            elif field and "too_long" in kind:
                messages.append(f"{field} is too long.")
            elif field:
                messages.append(f"{field} is not valid.")
    return " ".join(dict.fromkeys(messages)) or "Some of the information you entered is not valid."


def api_signup(username: str, email: str, password: str) -> str | None:
    """Real account creation (``POST /user/users``, body {username, email, password}).

    The backend answers 201 with the new profile and does NOT log the user in (no token): the caller
    redirects to the login page. The password is only used for this call. Returns an error message,
    or None when the account was created."""
    response = create_account(username, email, password)
    status, data = response["status_code"], response["data"]
    detail = data.get("detail") if isinstance(data, dict) else None
    if status == 201:
        return None
    if status == 409:
        text = str(detail or "").lower()
        if "email" in text:
            return "An account with this email address already exists."
        return "This username is already taken. Please choose another one."
    if status == 422:
        return _validation_message(detail)
    if status == 0:
        return "The server is unreachable right now. Please try again in a moment."
    return "We could not create your account right now. Please try again later."


def status_label() -> str:
    """Discreet indicator for the user menu."""
    if is_demo():
        return f"Demo mode — {display_name()}"
    return f"Logged in as {display_name()}"


def expire(message: str = "Your session has expired. Please log in again.") -> None:
    """The backend refused the token: back to the login page with an explanation."""
    logout()
    st.session_state["login_notice"] = message


def sign_out() -> None:
    """User-initiated logout: tells the backend (best effort) then clears the local session.

    ``POST /logout`` is documented but not implemented in the backend yet, so a failure (404...) is
    ignored: the token is always forgotten on this side."""
    token = st.session_state.get("access_token")
    if token and not is_demo():
        try:
            auth.logout(token)
        except Exception:  # noqa: BLE001 - never block a logout on the network
            pass
    logout()


def logout() -> None:
    """Forgets everything about the current session (local only)."""
    for key in _KEYS:
        st.session_state.pop(key, None)
    st.session_state.pop("demo_state", None)
