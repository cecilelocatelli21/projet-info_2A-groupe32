"""Users: search other readers by username and open their public profile.

``GET /users?username=<text>`` (token required) returns the users whose username contains the text,
case-insensitive, sorted by username; an empty text returns everyone. The answer is a list of
``UserPublicModel`` (user_id, username, bio): no e-mail, password or token ever reaches this page.
Clicking a result opens the public profile page, no follow needed.
"""

import streamlit as st

from data.errors import BusinessRuleError, DataUnavailable
from data.factory import get_repository
from ui import components as ui

repo = get_repository()
ui.navbar("users")
ui.page_header("Users", "Find other readers by their username and discover their library.")

if "user_search" not in repo.supports:
    ui.empty("User search unavailable", "Searching for users is not available in this mode.")
    st.stop()

if "users_q" not in st.session_state:
    st.session_state["users_q"] = ""


def clear_users() -> None:
    st.session_state["users_q"] = ""


query = ui.search_bar("users_q", "Search readers by username…", clear_users)

people, failure = [], None
with st.spinner("Searching…"):
    try:
        people = repo.search_users(query)
    except DataUnavailable as exc:
        failure = f"The server is not responding right now. ({exc})"
    except BusinessRuleError as exc:
        failure = str(exc)

if failure:
    ui.empty("Search unavailable", "Please try again in a moment.")
    st.caption(f"Technical detail: {failure}")
    st.button("Try again", key="users_retry")
elif people:
    n = len(people)
    st.caption(f"“{query}” — {n} user{'s' if n > 1 else ''}" if query else f"Everyone on Ex-Libris — {n} user{'s' if n > 1 else ''}")
    with st.container(key="people_grid", gap=None):
        for person in people:
            ui.person_row(person, "us")
elif query:
    ui.empty("No user found", f"Nobody has a username containing “{query}”.")
    st.button("Clear search", key="users_clear_empty", on_click=clear_users)
else:
    ui.empty("No users yet", "Nobody to show for the moment.")
