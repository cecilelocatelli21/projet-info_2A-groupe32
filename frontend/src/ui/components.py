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
    img = f"<img src='{escape(book.cover_url)}' loading='lazy' alt=''>" if book.cover_url else ""
    chip = status_chip(entry.status) if entry else ""
    detail = ""
    if info:
        rate = f"<span>★ {book.rating:.1f}</span> · " if book.rating else ""
        detail = (
            f"<div class='cv-info'><b>{escape(book.title)}</b>{rate}{escape(book.authors_label)}</div>"
        )
    return (
        f"<div class='cv' style='--h:{_hue(book.work_id)}'>"
        f"<div class='cv-art'><span class='cv-t'>{escape(book.title)}</span>"
        f"<span class='cv-a'>{escape(book.authors_label)}</span></div>{img}{chip}{detail}</div>"
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
                f"<span>{escape(book.authors_label)}</span></div>"
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
            if st.button("Mon profil", key="menu_profile", width="stretch"):
                st.switch_page(PAGES["profile"])
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


def review_card(review: Review) -> None:
    rating = f"<span class='stars'>{'★' * (review.rating or 0)}</span>" if review.rating else ""
    title = f" · <i>{escape(review.book_title)}</i>" if review.book_title else ""
    when = review.created.strftime("%d/%m/%Y") if review.created else ""
    html(
        f"<div class='panel'><span class='who'>{escape(review.author)}</span>{title}"
        f"<span class='when'>{when}</span> {rating}"
        f"<p>{escape(review.text)}</p>"
        f"<small style='color:var(--muted)'>♥ {review.likes}</small></div>"
    )


def safe(call, default=None):
    """Run a data call; show a friendly error (with the page still usable) if the API is down."""
    try:
        return call()
    except DataUnavailable as exc:
        empty("Serveur indisponible", "Impossible de joindre le serveur pour le moment.")
        st.caption(f"Détail technique : {exc}")
        return default
