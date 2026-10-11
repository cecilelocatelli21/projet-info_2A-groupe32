"""Helpers managing the logged-in user stored in Streamlit's session_state.

Two keys are used:
    access_token: the token returned by POST /login (read by utils.api_client)
    user: dictionary of the connected user (user_id, username, bio, email)
"""

import streamlit as st

TOKEN_KEY = "access_token"
USER_KEY = "user"

# Data tied to a user, erased on logout so that nothing leaks to the next login
_SESSION_KEYS = (
    TOKEN_KEY,
    USER_KEY,
    "book_query",
    "book_results",
    "user_query",
    "user_results",
    "flash",
)


def set_session(token: str, user: dict) -> None:
    """Stores the token and the connected user."""
    st.session_state[TOKEN_KEY] = token
    st.session_state[USER_KEY] = user


def get_current_user() -> dict | None:
    """Returns the connected user (dict), or None if nobody is logged in."""
    return st.session_state.get(USER_KEY)


def clear_session() -> None:
    """Forgets the token, the user and the data tied to them."""
    for key in _SESSION_KEYS:
        st.session_state.pop(key, None)
