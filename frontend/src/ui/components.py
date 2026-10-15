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
    "home": "views/home.py",
    "discover": "views/discover.py",
    "library": "views/library.py",
    "profile": "views/profile.py",
    "book": "views/book.py",
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
        if st.button(f"Ouvrir {book.title}", key=f"open_{scope}_{book.work_id}"):
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


def grid(key: str, entries: list[tuple[Book, LibraryEntry | None]], columns: int = 6) -> None:
    for start in range(0, len(entries), columns):
        cols = st.columns(columns, gap="medium")
        for col, (book, entry) in zip(cols, entries[start : start + columns], strict=False):
            with col:
                book_card(book, f"{key}{start}", entry, meta=True)


def empty(title: str, text: str) -> None:
    html(f"<div class='empty'><b>{escape(title)}</b>{escape(text)}</div>")


def page_header(title: str, subtitle: str = "") -> None:
    html(f"<h1 class='page-title'>{escape(title)}</h1>")
    if subtitle:
        html(f"<div class='page-sub'>{escape(subtitle)}</div>")


def source_banner(repo: Repository) -> None:
    if repo.degraded:
        html(
            "<div class='banner'>Le catalogue du serveur est indisponible : "
            "une sélection de livres de démonstration est affichée en attendant. "
            f"<small>({escape(repo.degraded_reason or '')})</small></div>"
        )


def navbar(current: str) -> None:
    """Top bar shared by every page. Typing in the search box leads to the discover page."""
    with st.container(horizontal=True, key="nav", vertical_alignment="center"):
        html("<div class='brand'><i></i>Ex-Libris</div>")
        st.page_link(PAGES["home"], label="Accueil")
        st.page_link(PAGES["discover"], label="Découvrir")
        st.page_link(PAGES["library"], label="Ma bibliothèque")
        st.page_link(PAGES["profile"], label="Profil")
        st.space("stretch")
        query = st.text_input(
            "Rechercher",
            key=f"nav_search_{current}",
            value=st.session_state.get("search_q", ""),
            placeholder="Rechercher un titre, un auteur…",
            label_visibility="collapsed",
            width=300,
        )
        if session.is_demo():
            html("<span class='demo-pill'>Démo</span>")
        with st.popover(session.display_name()[:1].upper()):
            html(f"<b>{escape(session.display_name())}</b>")
            html(f"<div class='session-state'>{escape(session.status_label())}</div>")
            if st.button("Mon profil", key="menu_profile", width="stretch"):
                open_profile(None)
            if session.is_demo() and st.button(
                "Réinitialiser la démo", key="menu_reset", width="stretch"
            ):
                st.session_state.pop("demo_state", None)
                st.rerun()
            if st.button("Se déconnecter", key="menu_logout", type="primary", width="stretch"):
                session.logout()
                st.rerun()
    if query != st.session_state.get("search_q", ""):
        st.session_state["search_q"] = query
        if query and current != "discover":
            st.switch_page(PAGES["discover"])


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
        <div class='hero-kicker'>À la une{' · ' + genres if genres else ''}</div>
        <h1>{escape(book.title)}</h1>
        <div class='hero-author'>{escape(book.authors_label)}{f' · {book.published}' if book.published else ''}</div>
        <div style='margin-bottom:.6rem'>{stars(book.rating, book.ratings_count)}</div>
        <div class='hero-desc'>{desc}</div></div>
        <div class='hero-cover'>{cover(book, info=False)}</div></div></div>"""
    )
    entry = repo.entry(book.work_id)
    with st.container(horizontal=True, key="hero_actions"):
        if st.button("▶  Découvrir le livre", type="primary", key="hero_open"):
            open_book(book.work_id)
        if entry:
            st.button("✓ Dans ma bibliothèque", key="hero_in", disabled=True)
        elif st.button("＋  Ajouter à ma bibliothèque", key="hero_add"):
            add_book(repo, book)
            st.rerun()


def add_book(repo: Repository, book: Book, status: str = "to read") -> bool:
    """Add to the library with user feedback. Returns True on success."""
    try:
        repo.add_to_library(book.work_id, status)
        st.toast(f"« {book.title} » ajouté à ta bibliothèque", icon="📚")
        return True
    except BusinessRuleError as exc:
        st.toast(str(exc), icon="⚠️")
    except DataUnavailable:
        st.toast("Le serveur ne répond pas, réessaie dans un instant.", icon="⚠️")
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


def review_card(review: Review, repo: Repository | None = None, scope: str = "r", book: Book | None = None) -> None:
    """A review: clickable author, rating, date, text and a like button tied to the connected user.

    With ``book`` (profile page) the cover is shown on the left and opens the book page."""
    with st.container(key=f"rev_{scope}_{review.review_id}"):
        left, right = st.columns([1, 6], gap="medium") if book else (None, st.container())
        if left is not None:
            with left:
                book_card(book, f"rv{scope}{review.review_id}")
        with right:
            with st.container(horizontal=True, vertical_alignment="center"):
                html(avatar(review.author or "?", small=True))
                user_link(review.author, review.author_id, f"ulink_{scope}_{review.review_id}")
                when = review.created.strftime("%d/%m/%Y") if review.created else ""
                rating = f"<span class='stars'>{'★' * review.rating}</span>" if review.rating else ""
                html(f"<span class='when'>{when}</span> {rating}")
            if book:
                html(f"<div class='rev-book'>{escape(book.title)}</div>")
            html(f"<p class='rev-text'>{escape(review.text)}</p>")
            can_like = repo is not None and "likes" in repo.supports and review.likeable
            if can_like and not review.is_mine:
                label = f"{'♥' if review.liked_by_me else '♡'} {review.likes}"
                if st.button(
                    label,
                    key=f"like_{scope}_{review.review_id}",
                    type="primary" if review.liked_by_me else "secondary",
                    help="Retirer mon like" if review.liked_by_me else "J'aime cette critique",
                ):
                    try:
                        repo.toggle_like(review)
                    except BusinessRuleError as exc:
                        st.toast(str(exc), icon="⚠️")
                    except DataUnavailable:
                        st.toast("Le serveur ne répond pas, réessaie dans un instant.", icon="⚠️")
                    st.rerun()
            else:
                html(f"<small style='color:var(--muted)'>♥ {review.likes}</small>")


def safe(call, default=None):
    """Run a data call; show a friendly error (with the page still usable) if the API is down."""
    try:
        return call()
    except DataUnavailable as exc:
        empty("Serveur indisponible", "Impossible de joindre le serveur pour le moment.")
        st.caption(f"Détail technique : {exc}")
        return default
