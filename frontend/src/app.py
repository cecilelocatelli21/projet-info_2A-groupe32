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
    pages = [
        st.Page("views/home.py", title="Accueil", icon="🏠", url_path="accueil", default=True),
        st.Page("views/discover.py", title="Découvrir", icon="🔎", url_path="decouvrir"),
        st.Page("views/library.py", title="Ma bibliothèque", icon="📚", url_path="bibliotheque"),
        st.Page("views/profile.py", title="Profil", icon="👤", url_path="profil"),
        st.Page("views/book.py", title="Fiche livre", icon="📖", url_path="livre"),
    ]
else:
    pages = [st.Page("views/login.py", title="Connexion", icon="📖", url_path="connexion", default=True)]

st.navigation(pages, position="hidden").run()
