"""Personal library: shelves by status, filters and sorting."""

import streamlit as st

from data.factory import get_repository
from data.models import STATUS_LABELS, STATUSES
from data.search import normalize
from ui import components as ui

repo = get_repository()
ui.navbar("library")
ui.page_header("My Library", "Your collection, and where you are in each book.")

entries = ui.safe(repo.library, [])
counts = {s: sum(e.status == s for e in entries) for s in STATUSES}

def clear_filter() -> None:
    st.session_state["library_q"] = ""


c1, c3 = st.columns([3, 1.1], vertical_alignment="top")
with c1:
    text = ui.search_bar("library_q", "Filter your library by title or author…", clear_filter)
sort = c3.selectbox(
    "Sort",
    ["added", "title", "rating"],
    format_func={"added": "Recently added", "title": "Title (A → Z)", "rating": "My rating"}.get,
    label_visibility="collapsed",
)


def visible(items):
    q = normalize(text)
    out = [
        e
        for e in items
        if (not q or q in normalize(e.book.title) or q in normalize(e.book.authors_label))
    ]
    if sort == "title":
        out.sort(key=lambda e: normalize(e.book.title))
    elif sort == "rating":
        out.sort(key=lambda e: -(e.rating or 0))
    else:
        out.sort(key=lambda e: e.date_added, reverse=True)
    return out


tabs = st.tabs([f"All · {len(entries)}"] + [f"{STATUS_LABELS[s]} · {counts[s]}" for s in STATUSES])
for tab, status in zip(tabs, [None, *STATUSES], strict=True):
    with tab:
        items = visible([e for e in entries if status is None or e.status == status])
        if items:
            ui.grid(f"lib{status or 'all'}".replace(" ", ""), [(e.book, e if status is None else None) for e in items])
        elif entries:
            ui.empty("Nothing here yet", "No book matches these filters.")
        else:
            ui.empty("Your library is empty", "Add your first book from Home or Discover.")
