"""Public home page, shown to visitors who are not logged in.

Book search and book details need a token in the backend (``GET /books/?q=`` and
``GET /books/{work_id}`` answer 401 without one), but ``GET /books/find_all/`` is public: the books
stored on the server (with their covers) are shown first. A built-in sample catalogue
(``DemoCatalog``) completes the page when the server has few books or cannot be reached; those
shelves say so. Clicking a card invites the visitor to create an account.
"""

from html import escape

import streamlit as st

from data import demo_catalog
from data.api_repository import _book
from data.demo_repository import DemoCatalog
from data.models import Book
from ui import components as ui
from utils.api_client import api_client
from utils.settings import data_source

ui.public_navbar("landing")


def server_books() -> list[Book]:
    """Books stored on the server (public route). Empty when it is unreachable. Cached per session."""
    if data_source() == "demo":
        return []
    if "_public_books" not in st.session_state:
        response = api_client.get("/books/find_all/")
        raw = response["data"] if response["status_code"] == 200 and isinstance(response["data"], list) else []
        st.session_state["_public_books"] = [_book(b) for b in raw if isinstance(b, dict) and b.get("work_id")]
    return st.session_state["_public_books"]


real = server_books()
catalog = DemoCatalog().catalog()
popular = sorted(catalog, key=lambda b: (-b.ratings_count, b.title))


def go_signup() -> None:
    st.session_state["signup_notice"] = "Create an account to open book pages and build your library."
    st.switch_page(ui.PAGES["signup"])


def sample_card(book: Book, scope: str) -> None:
    """A cover that invites the visitor to sign up (book pages need an account)."""
    with st.container(key=f"card_{scope}_{book.work_id}"):
        ui.html(ui.cover(book))
        if st.button(f"Open {book.title}", key=f"open_{scope}_{book.work_id}"):
            go_signup()


def sample_shelf(key: str, title: str, subtitle: str, books: list[Book]) -> None:
    if not books:
        return
    ui.html(f"<div class='shelf-title'>{escape(title)}</div><div class='shelf-sub'>{escape(subtitle)}</div>")
    with st.container(horizontal=True, key=f"row_{key}"):
        for book in books:
            sample_card(book, key)


# ---- hero --------------------------------------------------------------------------------------
# decorative background: real covers first, repeated, then sample covers if the server has few books
mosaic_books = (real * 8)[:24] if len(real) >= 8 else real + popular[: 24 - len(real)]
mosaic = "".join(ui.cover(b, info=False) for b in mosaic_books)
with st.container(key="lp_hero"):
    ui.html(f"<div class='lp-mosaic'>{mosaic}</div>")
    ui.html(
        """
        <div class='lp-kicker'>Your personal library</div>
        <h1 class='lp-title'>Every book you read <em>opens</em> the next.</h1>
        <div class='lp-sub'>Discover new reads, shelve them, follow your progress
        and share your reviews with other readers.</div>
        """
    )
    with st.container(horizontal=True, key="lp_actions"):
        if st.button("Create account", type="primary", key="hero_signup"):
            st.switch_page(ui.PAGES["signup"])
        if st.button("Log in", key="hero_login"):
            st.switch_page(ui.PAGES["login"])

# ---- shelves -----------------------------------------------------------------------------------
if real:
    sample_shelf(
        "lp_real",
        "On Ex-Libris",
        "Books readers have already added. Log in to search every book and open its page.",
        real[:20],
    )
sample_shelf(
    "lp_popular",
    "Popular with readers",
    "A sample selection to give you an idea of what you will find. Log in to browse everything.",
    popular[:14],
)
sample_shelf(
    "lp_classics",
    "Timeless classics",
    "Stories that have been opening the next book for generations.",
    [b for b in popular if demo_catalog.GENRE_CLASSICS in b.genres][:14],
)
sample_shelf(
    "lp_scifi",
    "Science Fiction & Fantasy",
    "Other worlds, one page away.",
    [b for b in popular if {demo_catalog.GENRE_SF, demo_catalog.GENRE_FANTASY} & set(b.genres)][:14],
)

# ---- what you can do ---------------------------------------------------------------------------
ui.html(
    """
    <div class='shelf-title'>Everything a reader needs</div>
    <div class='lp-feats'>
      <div class='lp-feat'><i>📚</i><b>Build your library</b>
        <p>Sort every book into Want to Read, Currently Reading, Read or Did Not Finish.</p></div>
      <div class='lp-feat'><i>⭐</i><b>Rate and review</b>
        <p>Give a book a rating once you have read it, write a review and like the reviews of others.</p></div>
      <div class='lp-feat'><i>👥</i><b>Follow other readers</b>
        <p>Browse public profiles, see what friends are reading and find your next favourite book.</p></div>
    </div>
    """
)

# ---- closing call to action --------------------------------------------------------------------
with st.container(key="lp_cta"):
    ui.html("<h2>Ready to start your library?</h2><div class='page-sub'>It only takes a minute to create your account.</div>")
    with st.container(horizontal=True, horizontal_alignment="center", key="lp_cta_actions"):
        if st.button("Create account", type="primary", key="cta_signup"):
            st.switch_page(ui.PAGES["signup"])
        if st.button("Log in", key="cta_login"):
            st.switch_page(ui.PAGES["login"])

ui.html("<div class='lp-foot'>© Ex-Libris · Discover, shelve and share the books you love.</div>")
