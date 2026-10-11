"""
Streamlit page for the main menu.

Provides navigation to the available actions for a logged-in user.
"""

import streamlit as st

from utils.session import get_current_user
from utils.ui import init_page, logout

logger = init_page("main_menu", "Main menu", "🏠")

user = get_current_user()

st.badge(f"Hello {user['username']}!", color="blue")

st.write("Available actions:")

if st.button("Search books"):
    st.switch_page("pages/search_books.py")
if st.button("My library"):
    st.switch_page("pages/library.py")
if st.button("Search users"):
    st.switch_page("pages/search_users.py")
if st.button("My profile"):
    st.switch_page("pages/profile.py")
if st.button("Log out", type="primary", key="menu_logout"):
    logout(logger)
