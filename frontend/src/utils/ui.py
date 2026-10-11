"""Shared UI helpers: page setup, sidebar, error handling and reusable cards."""

import logging

import streamlit as st

from api import auth
from utils.auth_guard import check_authentification
from utils.log_init import get_page_logger
from utils.session import clear_session, get_current_user

# Reading statuses, in the order of a reading life, with their display label
STATUS_LABELS = {
    "to read": "📌 To read",
    "in progress": "📖 In progress",
    "read": "✅ Read",
    "abandoned": "🚫 Abandoned",
}
READING_STATUSES = list(STATUS_LABELS)

# A rating is only accepted once the book is finished (or abandoned)
RATEABLE_STATUSES = ("read", "abandoned")


def status_label(status: str) -> str:
    """Display label of a reading status."""
    return STATUS_LABELS.get(status, status)


def init_page(
    page_name: str, title: str, icon: str, protected: bool = True, layout: str = "centered"
) -> logging.Logger:
    """Common start of every page: configuration, logger, access control, sidebar, title.

    Must be the first Streamlit call of a page.
    Args:
        page_name (str): name used by the logger (e.g. "library").
        title (str): title of the page.
        icon (str): emoji shown in the browser tab and before the title.
        protected (bool): if True, the user must be logged in, otherwise he is sent back home.
        layout (str): "centered" or "wide".
    Returns:
        logging.Logger: the logger of the page.
    """
    st.set_page_config(page_title=f"Ex-Libris - {title}", page_icon=icon, layout=layout)
    logger = get_page_logger(page_name)

    if protected:
        check_authentification()
        if get_current_user() is None:
            # A token without user: the session is incomplete, log in again
            clear_session()
            st.switch_page("pages/home.py")
        render_sidebar(logger)

    st.title(f"{icon} {title}")
    show_flash()
    return logger


def render_sidebar(logger: logging.Logger) -> None:
    """Navigation menu shown on every protected page."""
    user = get_current_user()
    with st.sidebar:
        st.markdown("### 📚 Ex-Libris")
        if user:
            st.caption(f"Signed in as **{user['username']}**")
        st.page_link("pages/main_menu.py", label="Menu", icon="🏠")
        st.page_link("pages/search_books.py", label="Search books", icon="🔎")
        st.page_link("pages/library.py", label="My library", icon="📚")
        st.page_link("pages/search_users.py", label="Search users", icon="👥")
        st.page_link("pages/profile.py", label="My profile", icon="👤")
        if st.button("Log out", type="primary", key="sidebar_logout"):
            logout(logger)


def logout(logger: logging.Logger) -> None:
    """Logs out: the token is erased in the backend, then in the session."""
    logger.info("Log out")
    auth.logout()  # best effort: even if it fails, the local session is cleared
    clear_session()
    st.switch_page("pages/home.py")


def flash(kind: str, message: str) -> None:
    """Keeps a message to display after the next rerun (st.rerun erases what was shown).
    Args:
        kind (str): "success", "info", "warning" or "error".
        message (str): the text to display.
    """
    st.session_state["flash"] = (kind, message)


def show_flash() -> None:
    """Displays (once) the message kept by flash()."""
    if "flash" in st.session_state:
        kind, message = st.session_state.pop("flash")
        getattr(st, kind)(message)


def error_detail(data) -> str:
    """Readable text from the body of an error response (FastAPI 'detail')."""
    detail = data.get("detail") if isinstance(data, dict) else data
    if isinstance(detail, list):  # 422 validation errors
        return "; ".join(str(e.get("msg", e)) if isinstance(e, dict) else str(e) for e in detail)
    return str(detail) if detail else "Unexpected error"


def show_api_error(response: dict, logger: logging.Logger, action: str) -> None:
    """Displays a clear message for a failed API call and logs it.

    An expired or invalid token (401) logs the user out and goes back to the home page.
    Args:
        response (dict): dictionary returned by the api_client.
        logger (logging.Logger): the logger of the page.
        action (str): what was attempted, e.g. "load the library".
    """
    status = response["status_code"]
    data = response["data"]
    logger.error(f"Could not {action}: {status} {data}")

    if status == 401:
        clear_session()
        flash("warning", "Your session has expired, please log in again.")
        st.switch_page("pages/home.py")
    elif status == 0:
        st.error(f"Cannot reach the server ({data}). Is the backend running?")
    elif status == 503:
        st.error("OpenLibrary is unreachable at the moment, please try again later.")
    else:
        st.error(f"Could not {action}: {error_detail(data)}")


def parse_id(value) -> int | None:
    """Converts a query parameter to an int, None if it is missing or not a number."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def render_book(book: dict) -> None:
    """Card of a book (search result): cover, title, authors and a link to its page."""
    with st.container(border=True):
        col_cover, col_info, col_link = st.columns([1, 5, 2], vertical_alignment="center")
        with col_cover:
            if book.get("cover_url"):
                st.image(book["cover_url"], width=70)
            else:
                st.markdown("## 📕")
        with col_info:
            st.markdown(f"**{book.get('title') or 'Untitled'}**")
            st.caption(book.get("authors") or "Unknown author")
        with col_link:
            if book.get("work_id"):
                st.page_link(
                    "pages/book_details.py",
                    label="Details",
                    icon="📖",
                    query_params={"work_id": book["work_id"]},
                )


def render_user(user: dict) -> None:
    """Card of a user (public data only): username, bio and a link to his profile."""
    with st.container(border=True):
        col_info, col_link = st.columns([5, 2], vertical_alignment="center")
        with col_info:
            st.markdown(f"**{user['username']}**")
            st.caption(user.get("bio") or "No bio yet")
        with col_link:
            st.page_link(
                "pages/profile.py",
                label="Profile",
                icon="👤",
                query_params={"user_id": user["user_id"]},
            )
