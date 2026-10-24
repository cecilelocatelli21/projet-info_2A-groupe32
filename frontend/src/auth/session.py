"""Session handling: real login / signup / logout, plus the demo login isolated so it can be removed.

To switch to real authentication only: set ``EXLIBRIS_ENABLE_DEMO_LOGIN=false``. The demo mode
then disappears from the login page; ``api_login`` (real POST /login) stays.
"""

from __future__ import annotations

import streamlit as st

from api import auth
from api.users import change_password, create_account, delete_account, update_profile
from data import demo_catalog
from utils.api_client import api_client

# Technical keys that survive a logout (logging set-up). Everything else belongs to the session of the
# user who has just left (token, identity, search text, cached books, flash messages...) and is erased.
_KEEP = {"logs_initialized", "logger", "last_navigated_page"}


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
    """Confirms that the token opens a protected route (GET /users/{id} needs a Bearer token).

    True = accepted, False = refused (401), None = inconclusive (server error, route unavailable)."""
    response = api_client.get(f"/users/{user_id}", headers={"Authorization": f"Bearer {token}"})
    status = response["status_code"]
    if status == 200:
        return True
    return False if status == 401 else None


def api_login(username: str, password: str) -> str | None:
    """Real login: ``POST /login`` with the JSON body {username, password}.

    The backend answers {"id_user", "username", "access_token"}. The password is only used for this
    call: it is neither stored nor logged. Returns an error message, or None on success."""
    response = auth.login(username, password)
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
    """Real account creation (``POST /users``, body {username, email, password}).

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
    """User-initiated logout.

    1. ``POST /logout`` erases the token in the backend (best effort: a failure never blocks the logout).
    2. Everything kept for this session is erased (see ``logout``)."""
    token = st.session_state.get("access_token")
    if token and not is_demo():
        try:
            auth.logout(token)
        except Exception:  # noqa: BLE001 - never block a logout on the network
            pass
    logout()


def logout() -> None:
    """Forgets everything about the current session (local only): token, identity, search text, cached
    books and reviews, messages. Only the logging set-up is kept, so nothing private can be shown to
    the next visitor of the same browser tab."""
    for key in list(st.session_state.keys()):
        if key not in _KEEP:
            try:
                del st.session_state[key]
            except Exception:  # noqa: BLE001 - a widget key that cannot be removed now is dropped on rerun
                pass


def notify_visitor(message: str) -> None:
    """Message shown once on the public pages (e.g. after deleting an account)."""
    st.session_state["public_notice"] = message


# ---- account management (all calls use the connected user's own id and token) ------------------------
def _account_error(response: dict, what: str) -> str:
    """Readable message for a failed account call; a 401 ends the session."""
    status, data = response["status_code"], response["data"]
    detail = data.get("detail") if isinstance(data, dict) else None
    if status == 401:
        expire()
        return "Your session has expired. Please log in again."
    if status == 404:
        return "This account no longer exists."
    if status == 403:
        return "You can only modify your own account."
    if status == 0:
        return "The server is unreachable right now. Please try again in a moment."
    if status in (400, 409) and detail:
        return str(detail)
    if status == 422:
        return _validation_message(detail)
    return f"Could not {what}: the server returned an error ({status}). Please try again later."


def api_update_profile(bio: str | None = None, email: str | None = None) -> str | None:
    """``PUT /users/{id}`` for the connected user. Returns an error message, or None on success."""
    response = update_profile(st.session_state["user_id"], bio=bio, email=email)
    if response["status_code"] == 200:
        return None
    if response["status_code"] == 409:
        return "This email address is already used by another account."
    return _account_error(response, "update your profile")


def api_change_password(old_password: str, new_password: str) -> str | None:
    """``PUT /users/{id}/password`` for the connected user. The passwords are only sent, never kept."""
    response = change_password(st.session_state["user_id"], old_password, new_password)
    if response["status_code"] == 204:
        return None
    if response["status_code"] == 400:
        return "Your current password is incorrect."
    return _account_error(response, "change your password")


def api_delete_account() -> str | None:
    """``DELETE /users/{id}`` for the connected user (the id comes from the session, never from input).

    On success the local session is erased and a confirmation is queued for the public home page."""
    response = delete_account(st.session_state["user_id"])
    if response["status_code"] == 204:
        logout()
        notify_visitor("Your account has been permanently deleted.")
        return None
    return _account_error(response, "delete your account")
