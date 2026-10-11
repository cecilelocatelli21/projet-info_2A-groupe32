"""
Streamlit page for searching users by username.

Each result links to the profile of the user.

Endpoint used:
    GET /users?username=
"""

import streamlit as st

from api import users
from utils.ui import init_page, render_user, show_api_error

logger = init_page("search_users", "Search users", "👥")

with st.form("search_users_form"):
    query = st.text_input(
        "Username", value=st.session_state.get("user_query", ""), placeholder="Part of a username"
    )
    submitted = st.form_submit_button("Search")

if submitted:
    logger.info(f"Search users: '{query}'")
    response = users.search_users(query.strip())
    if response["status_code"] == 200:
        st.session_state["user_query"] = query.strip()
        st.session_state["user_results"] = response["data"]
    else:
        st.session_state.pop("user_results", None)
        show_api_error(response, logger, "search users")

results = st.session_state.get("user_results")
if results is not None:
    if results:
        st.caption(f"{len(results)} user(s) found")
        for found in results:
            render_user(found)
    else:
        st.info("No user found.")

if st.button("Back to menu", type="primary"):
    st.switch_page("pages/main_menu.py")
