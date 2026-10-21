"""Discover & search: text search (navbar), genre/author filters, sorting, cover grid."""

import streamlit as st

from data.errors import DataUnavailable
from data.factory import get_repository
from data.search import SORT_LABELS
from ui import components as ui

repo = get_repository()
ui.navbar("discover")
ui.page_header("Discover", "Search for a title or an author, or explore by genre.")

query = st.session_state.get("search_q", "").strip()
remote = repo.source == "api" and bool(query)  # keyword search = GET /books?q=...
failure = None  # set when the backend cannot answer: shown once, never mistaken for "no result"

found = []
if remote:
    with st.spinner("Searching…"):
        try:
            found = repo.search(query)
        except DataUnavailable as exc:
            failure = exc

c1, c2, c3 = st.columns([2, 2, 1.2])
if remote:
    # OpenLibrary results carry no genre: only the authors found are offered as a filter
    genres = []
    c1.multiselect("Genres", [], placeholder="Genres: not provided by search results", disabled=True)
    author_options = sorted({a for b in found for a in b.authors})
else:
    genres = c1.multiselect("Genres", ui.safe(repo.genres, []), placeholder="All genres")
    author_options = ui.safe(repo.authors, [])
authors = c2.multiselect("Authors", author_options, placeholder="All authors")
sort = c3.selectbox("Sort by", list(SORT_LABELS), format_func=SORT_LABELS.get)

results = []
if failure is None:
    with st.spinner("Loading…"):
        try:
            results = repo.search(query, genres, authors, sort)
        except DataUnavailable as exc:
            failure = exc
ui.source_banner(repo)

if failure is not None:
    ui.empty("Search unavailable", "The server is not responding right now. Please try again in a moment.")
    st.caption(f"Technical detail: {failure}")
    st.button("Try again")
elif results:
    st.caption(f"{'“' + query + '” — ' if query else ''}{len(results)} book{'s' if len(results) != 1 else ''}")
    ui.grid("disc", [(b, repo.entry(b.work_id) if repo.source == "demo" else None) for b in results])
else:
    st.caption(f"“{query}” — 0 books" if query else "")
    ui.empty("No books found", "Try another title or keyword, or remove a filter." if query else "The catalogue is empty for now.")
    if query:
        st.button("Clear search", on_click=ui.clear_search)
