"""Discover: one search bar (title or author) and a grid of covers.

The text goes to ``GET /books/?q=<text>`` (the "Search Books" route): the backend forwards it as
``q`` to Open Library, which looks for it in titles and author names. Without text the books already
stored on the server (``GET /books/find_all/``) are listed. There is no genre, author or date filter:
the local ``Book`` model only holds a title and an author.

The text is sent 450 ms after the last keystroke (a small script of the search bar; Enter sends it at once).
Streamlit cancels a run that is superseded by a newer one, so the answer to an older text can never replace
the results of the latest one, and answers are kept per session: the backend is not called again for a text
already searched.
"""

import streamlit as st

from data.errors import DataUnavailable
from data.factory import get_repository
from ui import components as ui

repo = get_repository()
ui.navbar("discover")
ui.page_header("Discover", "Find your next read by title or by author.")

# the text typed in the navbar of another page arrives here through "search_q"
if "discover_q" not in st.session_state:
    st.session_state["discover_q"] = st.session_state.get("search_q", "")


def clear_search() -> None:
    st.session_state["discover_q"] = ""
    st.session_state["search_q"] = ""


query = ui.search_bar("discover_q", "Search by book title or author…", clear_search)
st.session_state["search_q"] = query

results, failure = [], None
with st.spinner("Searching…" if query else "Loading books…"):
    try:
        results = repo.search(query)
    except DataUnavailable as exc:
        failure = exc
ui.source_banner(repo)

if failure is not None:
    ui.empty(
        "Search unavailable" if query else "Books unavailable",
        "The server is not responding right now (Open Library may be unreachable). Please try again in a moment.",
    )
    st.caption(f"Technical detail: {failure}")
    st.button("Try again", key="discover_retry")
elif results:
    n = len(results)
    st.caption(f"“{query}” — {n} book{'s' if n > 1 else ''}" if query else f"On Ex-Libris — {n} book{'s' if n > 1 else ''}")
    ui.grid("disc", [(b, repo.entry(b.work_id) if repo.source == "demo" else None) for b in results])
elif query:
    st.caption(f"“{query}” — 0 books")
    ui.empty("No book found", "Try another title, another author or fewer words.")
    st.button("Clear search", key="discover_clear_empty", on_click=clear_search)
else:
    ui.empty("No books yet", "The server has no book to show for the moment. Search for a title or an author above.")
