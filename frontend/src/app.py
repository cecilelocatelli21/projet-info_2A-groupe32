"""Ex-Libris front-end entry point (Streamlit).

Launch: ``cd frontend && uv run --project . streamlit run src/app.py``
"""

import streamlit as st

st.set_page_config(page_title="Ex-Libris", page_icon="📖", layout="wide", initial_sidebar_state="collapsed")

from auth import session  # noqa: E402
from ui.theme import inject_css  # noqa: E402
from utils.env_variables import display_values, load_environment_variables  # noqa: E402
from utils.log_init import get_page_logger, initialize_logs  # noqa: E402

if "logs_initialized" not in st.session_state:
    initialize_logs("Streamlit App")
    load_environment_variables()
    display_values(include_prefix="BACKEND")
    st.session_state["logs_initialized"] = True
get_page_logger("exlibris")

inject_css()

if session.is_logged_in():
    # logged-in user: the whole app (the visitor pages are not registered, so they cannot be opened)
    pages = [
        st.Page("views/home.py", title="Home", icon="🏠", url_path="home", default=True),
        st.Page("views/discover.py", title="Discover", icon="🔎", url_path="discover"),
        st.Page("views/library.py", title="My Library", icon="📚", url_path="library"),
        st.Page("views/profile.py", title="Profile", icon="👤", url_path="profile"),
        st.Page("views/book.py", title="Book", icon="📖", url_path="book"),
    ]
else:
    # visitor: public landing page (default), login and account creation. Protected pages are not
    # registered here, so a logged-out user typing /library lands on the public home page.
    pages = [
        st.Page("views/landing.py", title="Ex-Libris", icon="📖", url_path="welcome", default=True),
        st.Page("views/login.py", title="Log in", icon="🔑", url_path="login"),
        st.Page("views/signup.py", title="Create account", icon="✨", url_path="signup"),
    ]

st.navigation(pages, position="hidden").run()
