"""Reusable UI building blocks: navbar, hero banner, shelves, cards, chips, stars..."""

from __future__ import annotations

import zlib
from html import escape

import streamlit as st

from auth import session
from data.errors import BusinessRuleError, DataUnavailable
from data.models import STATUS_LABELS, Book, LibraryEntry, Review
from data.repository import Repository

PAGES = {
    "landing": "views/landing.py",
    "login": "views/login.py",
    "signup": "views/signup.py",
    "home": "views/home.py",
    "discover": "views/discover.py",
    "library": "views/library.py",
    "profile": "views/profile.py",
    "book": "views/book.py",
    "users": "views/users.py",
    "edit_profile": "views/edit_profile.py",
}


def html(markup: str) -> None:
    """Render raw HTML. Lines are joined: Markdown would turn indented lines into code blocks."""
    flat = " ".join(line.strip() for line in markup.strip().splitlines())
    st.markdown(flat, unsafe_allow_html=True)


def _hue(key: str) -> int:
    return zlib.crc32(key.encode()) % 360


def stars(rating: float | None, count: int = 0) -> str:
    if not rating:
        return ""
    full = round(rating)
    on, off = "★" * full, "★" * (5 - full)
    tail = f" <small style='color:var(--muted)'>{rating:.1f}" + (f" · {count:,}".replace(",", " ") if count else "") + "</small>"
    return f"<span class='stars'>{on}<span class='off'>{off}</span></span>{tail}"


def status_chip(status: str) -> str:
    return f"<span class='chip s-{status.replace(' ', '-')}'>{STATUS_LABELS.get(status, status)}</span>"


def cover(book: Book, entry: LibraryEntry | None = None, info: bool = True) -> str:
    """Cover with a generated artwork underneath: a missing image never shows as a broken one."""
    img = ""
    url = (book.cover_url or "").strip()
    if url.lower().startswith(("http://", "https://")):
        # A CSS background (not an <img>): when the image cannot be loaded nothing is drawn, so the
        # generated artwork underneath stays visible instead of a broken-image icon.
        safe = url.translate({ord(c): f"%{ord(c):02X}" for c in "'\"()<> \n\r\t"})
        img = f"<div class='cv-img' style=\"background-image:url('{escape(safe)}')\"></div>"
    chip = status_chip(entry.status) if entry else ""
    detail = ""
    if info:
        rate = f"<span>★ {book.rating:.1f}</span> · " if book.rating else ""
        author = escape(", ".join(book.authors))  # nothing invented when the backend gives no author
        detail = f"<div class='cv-info'><b>{escape(book.title)}</b>{rate}{author}</div>"
    return (
        f"<div class='cv' style='--h:{_hue(book.work_id)}'>"
        f"<div class='cv-art'><span class='cv-t'>{escape(book.title)}</span>"
        f"<span class='cv-a'>{escape(', '.join(book.authors))}</span></div>{img}{chip}{detail}</div>"
    )


def open_book(work_id: str) -> None:
    st.session_state["selected_work"] = work_id
    st.switch_page(PAGES["book"])


def book_card(book: Book, scope: str, entry: LibraryEntry | None = None, meta: bool = False) -> None:
    """A clickable cover (the whole card is the button)."""
    with st.container(key=f"card_{scope}_{book.work_id}"):
        html(cover(book, entry))
        if meta:
            html(
                f"<div class='card-meta'><b>{escape(book.title)}</b>"
                f"<span>{escape(', '.join(book.authors))}</span></div>"
            )
        if st.button(f"Open {book.title}", key=f"open_{scope}_{book.work_id}"):
            open_book(book.work_id)


def shelf(key: str, title: str, books: list[Book], subtitle: str | None = None, repo=None) -> None:
    if not books:
        return
    html(f"<div class='shelf-title'>{escape(title)}</div>")
    if subtitle:
        html(f"<div class='shelf-sub'>{escape(subtitle)}</div>")
    with st.container(horizontal=True, key=f"row_{key}"):
        for book in books:
            entry = repo.entry(book.work_id) if repo and repo.source == "demo" else None
            book_card(book, key, entry)


def grid(key: str, entries: list[tuple[Book, LibraryEntry | None]], columns: int | None = None) -> None:
    """Covers in a responsive CSS grid (see ``st-key-grid_`` in theme.py): the number of columns follows the
    width of the page, every cell has the same width, the gaps are regular both ways, and a hovered cover
    grows inside its gap without moving or hiding its neighbours. Cover only: the title and the author
    appear on the cover itself (hover / touch). ``columns`` is kept for compatibility and ignored."""
    with st.container(horizontal=True, key=f"grid_{key}", gap=None):
        for book, entry in entries:
            book_card(book, key, entry)


def empty(title: str, text: str) -> None:
    html(f"<div class='empty'><b>{escape(title)}</b>{escape(text)}</div>")


def page_header(title: str, subtitle: str = "") -> None:
    html(f"<h1 class='page-title'>{escape(title)}</h1>")
    if subtitle:
        html(f"<div class='page-sub'>{escape(subtitle)}</div>")


def source_banner(repo: Repository) -> None:
    if repo.degraded:
        html(
            "<div class='banner'>The server catalogue is unavailable: "
            "a selection of demo books is shown in the meantime. "
            f"<small>({escape(repo.degraded_reason or '')})</small></div>"
        )


def navbar(current: str) -> None:
    """Top bar shared by every page. Typing in the search box leads to the discover page."""
    with st.container(horizontal=True, key="nav", vertical_alignment="center"):
        html("<div class='brand'><i></i>Ex-Libris</div>")
        st.page_link(PAGES["home"], label="Home")
        st.page_link(PAGES["discover"], label="Discover")
        st.page_link(PAGES["library"], label="My Library")
        st.page_link(PAGES["users"], label="Users")
        st.page_link(PAGES["profile"], label="Profile")
        st.space("stretch")
        # Discover has its own (single) search bar: no second one in the navbar there
        query = (
            st.session_state.get("search_q", "")
            if current == "discover"
            else st.text_input(
                "Search",
                key=f"nav_search_{current}",
                value=st.session_state.get("search_q", ""),
                placeholder="Search books by title or author…",
                label_visibility="collapsed",
                width=300,
            )
        )
        if session.is_demo():
            html("<span class='demo-pill'>Demo</span>")
        with st.popover(session.display_name()[:1].upper()):
            html(f"<b>{escape(session.display_name())}</b>")
            html(f"<div class='session-state'>{escape(session.status_label())}</div>")
            if st.button("My profile", key="menu_profile", width="stretch"):
                open_profile(None)
            if not session.is_demo() and st.button("Edit profile", key="menu_edit_profile", width="stretch"):
                st.switch_page(PAGES["edit_profile"])
            if session.is_demo() and st.button(
                "Reset demo", key="menu_reset", width="stretch"
            ):
                st.session_state.pop("demo_state", None)
                st.rerun()
            if st.button("Log out", key="menu_logout", type="primary", width="stretch"):
                session.sign_out()
                st.rerun()  # app.py now registers the visitor pages: the public home opens
    if query != st.session_state.get("search_q", ""):
        st.session_state["search_q"] = query
        if query and current != "discover":
            st.switch_page(PAGES["discover"])


def public_navbar(current: str) -> None:
    """Top bar for visitors (not logged in): brand, Log in, Create account."""
    with st.container(horizontal=True, key="nav", vertical_alignment="center"):
        html("<div class='brand'><i></i>Ex-Libris</div>")
        if current != "landing":
            st.page_link(PAGES["landing"], label="Home")
        st.space("stretch")
        if current != "login":
            st.page_link(PAGES["login"], label="Log in")
        if current != "signup":
            if st.button("Create account", key="nav_signup", type="primary"):
                st.switch_page(PAGES["signup"])


_DEBOUNCE_JS = """
(function () {
  if (window.__exlDebounce) return;
  window.__exlDebounce = true;
  var timer;
  document.addEventListener('input', function (e) {
    var el = e.target;
    if (!el.matches || !el.matches('[class*="st-key-searchbar_"] input')) return;
    clearTimeout(timer);
    timer = setTimeout(function () {
      if (document.activeElement !== el) return;
      ['keydown', 'keypress', 'keyup'].forEach(function (type) {
        el.dispatchEvent(new KeyboardEvent(type, {key: 'Enter', code: 'Enter', keyCode: 13, charCode: 13, which: 13, bubbles: true, cancelable: true}));
      });
    }, 450);
  }, true);
})();
"""


def search_bar(key: str, placeholder: str, on_clear) -> str:
    """The one search field of the application (Discover, Users): a rounded field with a small icon, no
    frame around it, a clear button that only exists while there is text, and a short delay (debounce)
    after the last keystroke before the text is sent; Enter sends it at once. Returns the trimmed text."""
    with st.container(key=f"searchbar_{key}", gap=None):
        st.text_input("Search", key=key, placeholder=placeholder, label_visibility="collapsed")
        if st.session_state.get(key):
            st.button("✕", key=f"{key}_clear", type="tertiary", on_click=on_clear, help="Clear search")
    st.html(f"<script>{_DEBOUNCE_JS}</script>", unsafe_allow_javascript=True)
    return (st.session_state.get(key) or "").strip()


def clear_search() -> None:
    st.session_state["search_q"] = ""
    st.session_state["nav_search_discover"] = ""


def hero(book: Book, repo: Repository) -> None:
    bg = (
        f"<div class='hero-bg' style=\"background-image:url('{escape(book.cover_url)}')\"></div>"
        if book.cover_url
        else f"<div class='hero-bg gen' style='background:linear-gradient(135deg,hsl({_hue(book.work_id)} 50% 26%),#0c0b10)'></div>"
    )
    desc = escape(book.description or "")
    genres = " · ".join(escape(g) for g in book.genres[:2])
    html(
        f"""<div class='hero'>{bg}<div class='hero-in'><div class='hero-copy'>
        <div class='hero-kicker'>Featured{' · ' + genres if genres else ''}</div>
        <h1>{escape(book.title)}</h1>
        <div class='hero-author'>{escape(book.authors_label)}{f' · {book.published}' if book.published else ''}</div>
        <div style='margin-bottom:.6rem'>{stars(book.rating, book.ratings_count)}</div>
        <div class='hero-desc'>{desc}</div></div>
        <div class='hero-cover'>{cover(book, info=False)}</div></div></div>"""
    )
    entry = repo.entry(book.work_id)
    with st.container(horizontal=True, key="hero_actions"):
        if st.button("▶  View book", type="primary", key="hero_open"):
            open_book(book.work_id)
        if entry:
            st.button("✓ In my library", key="hero_in", disabled=True)
        elif st.button("＋  Add to my library", key="hero_add"):
            add_book(repo, book)
            st.rerun()


def add_book(repo: Repository, book: Book, status: str = "to read") -> bool:
    """Add to the library with user feedback. Returns True on success."""
    try:
        repo.add_to_library(book.work_id, status)
        st.toast(f"“{book.title}” added to your library", icon="📚")
        return True
    except BusinessRuleError as exc:
        st.toast(str(exc), icon="⚠️")
    except DataUnavailable:
        st.toast("The server is not responding. Please try again in a moment.", icon="⚠️")
    return False


def open_profile(user_id: int | None) -> None:
    """Go to the public profile of ``user_id`` (own profile when it is the connected user)."""
    if user_id is None or user_id == st.session_state.get("user_id"):
        st.switch_page(PAGES["profile"])
    st.switch_page(PAGES["profile"], query_params={"user": str(user_id)})


def avatar(name: str, small: bool = False) -> str:
    return f"<div class='avatar{' sm' if small else ''}'>{escape(name[:1].upper())}</div>"


def user_link(name: str, user_id: int | None, key: str) -> None:
    """A username that really navigates to the user's profile (a button styled as a link)."""
    if user_id is None:
        html(f"<b>{escape(name)}</b>")
    elif st.button(f"@{name}", key=key, type="tertiary"):
        open_profile(user_id)


def person_row(person, scope: str) -> None:
    with st.container(horizontal=True, vertical_alignment="center", key=f"person_{scope}_{person.user_id}"):
        html(avatar(person.username, small=True))
        with st.container(gap=None):
            user_link(person.username, person.user_id, f"plink_{scope}_{person.user_id}")
            if person.bio:
                html(f"<span style='color:var(--muted);font-size:.8rem'>{escape(person.bio)}</span>")


def _failure_toast(exc: Exception) -> None:
    if isinstance(exc, DataUnavailable):
        st.toast("The server is not responding. Please try again in a moment.", icon="⚠️")
    else:
        st.toast(str(exc), icon="⚠️")


@st.dialog("Edit your review", width="medium")
def edit_review_dialog(review: Review, repo: Repository) -> None:
    """Edit form for the connected user's own review, prefilled with its current text and rating.

    Save changes calls ``PUT /review/reviews/{id}`` (never creates another review) and Cancel just closes
    the window. On an error the window stays open with the message and nothing is shown as saved."""
    if review.book_title:
        html(f"<div class='rev-book'>{escape(review.book_title)}</div>")
    rating = st.feedback("stars", key=f"edit_stars_{review.review_id}", default=(review.rating - 1) if review.rating else None)
    text = st.text_area(
        "Your review",
        value=review.text,
        key=f"edit_text_{review.review_id}",
        height=170,
        max_chars=2000,
        label_visibility="collapsed",
        placeholder="What did you think of this book?",
    )
    problem = st.empty()
    save, cancel = st.columns(2)
    if cancel.button("Cancel", key=f"edit_cancel_{review.review_id}", width="stretch"):
        st.rerun()  # closes the dialog; nothing was sent
    if save.button("Save changes", key=f"edit_save_{review.review_id}", type="primary", width="stretch"):
        if not text.strip():
            problem.warning("Your review cannot be empty.")
            return
        try:
            with st.spinner("Saving…"):
                repo.update_review(review, None if rating is None else rating + 1, text)
        except (BusinessRuleError, DataUnavailable) as exc:
            problem.error(str(exc) if isinstance(exc, BusinessRuleError) else "The server is not responding. Please try again in a moment.")
            return
        st.toast("Review updated", icon="✍️")
        st.rerun()


def review_card(review: Review, repo: Repository | None = None, scope: str = "r", book: Book | None = None) -> None:
    """One review: author (opens the profile), date, stars, text, then the actions.

    Every review shares the same layout; the connected user's own reviews only get an accent (see
    ``_mine`` in theme.py), a "You" tag and the discreet "Edit review" action, which is shown only for
    them (the backend refuses anyone else anyway: 403). With ``book`` (profile page) the cover is shown on
    the left and opens the book page."""
    suffix = "_mine" if review.is_mine else ""
    with st.container(key=f"rev_{scope}_{review.review_id}{suffix}"):
        left, right = st.columns([1, 6], gap="medium") if book else (None, st.container())
        if left is not None:
            with left:
                book_card(book, f"rv{scope}{review.review_id}")
        with right:
            with st.container(horizontal=True, vertical_alignment="center", gap="small"):
                html(avatar(review.author or "?", small=True))
                user_link(review.author, review.author_id, f"ulink_{scope}_{review.review_id}")
                if review.is_mine:
                    html("<span class='you-tag'>You</span>")
                st.space("stretch")
                if review.rating:
                    html(f"<span class='stars'>{'★' * review.rating}<span class='off'>{'★' * (5 - review.rating)}</span></span>")
                if review.created:
                    html(f"<span class='when'>{review.created.strftime('%b %d, %Y')}</span>")
            if book:
                html(f"<div class='rev-book'>{escape(book.title)}</div>")
            html(f"<p class='rev-text'>{escape(review.text)}</p>")
            can_like = repo is not None and "likes" in repo.supports and review.likeable
            with st.container(horizontal=True, vertical_alignment="center", gap="small", key=f"revact_{scope}_{review.review_id}"):
                if review.is_mine:
                    html(f"<span class='like-count'>♥ {review.likes}</span>")
                    if repo is not None and st.button("✎  Edit review", key=f"edit_{scope}_{review.review_id}", type="tertiary"):
                        edit_review_dialog(review, repo)
                elif can_like:
                    label = f"{'♥' if review.liked_by_me else '♡'} {review.likes}"
                    if st.button(
                        label,
                        key=f"like_{scope}_{review.review_id}",
                        type="primary" if review.liked_by_me else "secondary",
                        help="Remove my like" if review.liked_by_me else "Like this review",
                    ):
                        try:
                            repo.toggle_like(review)
                        except (BusinessRuleError, DataUnavailable) as exc:
                            _failure_toast(exc)
                        st.rerun()
                else:
                    html(f"<span class='like-count'>♥ {review.likes}</span>")


def safe(call, default=None):
    """Run a data call; show a friendly error (with the page still usable) if the API is down."""
    try:
        return call()
    except DataUnavailable as exc:
        empty("Server unavailable", "We cannot reach the server right now.")
        st.caption(f"Technical detail: {exc}")
        return default
