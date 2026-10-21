"""Book detail page: info, library actions, rating & review, other readers' reviews."""

from html import escape

import streamlit as st

from data.errors import BusinessRuleError, DataUnavailable
from data.factory import get_repository
from data.models import RATING_STATUSES, STATUS_LABELS, STATUSES
from ui import components as ui

repo = get_repository()
ui.navbar("book")

work_id = st.session_state.get("selected_work")
book = ui.safe(lambda: repo.get_book(work_id), None) if work_id else None
if book is None:
    ui.empty("Book not found", "Go back to Home to pick a book.")
    st.page_link(ui.PAGES["home"], label="← Back to Home")
    st.stop()

entry = ui.safe(lambda: repo.entry(work_id))
if st.button("← Back", key="back"):
    st.switch_page(ui.PAGES["home"])

left, right = st.columns([1, 2.4], gap="large")
with left:
    ui.html(f"<div style='max-width:320px'>{ui.cover(book, entry, info=False)}</div>")

with right:
    chips = "".join(f"<span class='chip'>{escape(g)}</span>" for g in book.genres)
    ui.html(f"<div>{chips}</div><h1 class='book-title'>{escape(book.title)}</h1>")
    ui.html(f"<div class='hero-author'>{escape(book.authors_label)}</div>")
    ui.html(f"<div>{ui.stars(book.rating, book.ratings_count) or '<small style=color:var(--muted)>No rating yet</small>'}</div>")
    ui.html(
        f"<p style='color:#d9d3e0;line-height:1.65;max-width:720px;margin-top:1rem'>"
        f"{escape(book.description or 'No description available for this book.')}</p>"
    )
    facts = [
        ("Published", book.published),
        ("Pages", book.pages),
        ("Publisher", book.publisher),
        ("ISBN", book.isbn),
    ]
    cells = "".join(f"<div><span>{k}</span><b>{escape(str(v))}</b></div>" for k, v in facts if v)
    if cells:
        ui.html(f"<div class='meta-grid'>{cells}</div>")

    st.markdown("##### My reading")
    try:
        if entry is None:
            c1, c2 = st.columns([1.2, 1.4])
            status = c2.selectbox(
                "Status", STATUSES, format_func=STATUS_LABELS.get, label_visibility="collapsed", key="add_status"
            )
            if c1.button("＋  Add to my library", type="primary", width="stretch"):
                if ui.add_book(repo, book, status):
                    st.rerun()
        else:
            ui.html(f"Current status: {ui.status_chip(entry.status)}")
            new = st.segmented_control(
                "Change status", STATUSES, default=entry.status, format_func=STATUS_LABELS.get,
                key=f"seg_{work_id}_{entry.status}",
            )
            if new and new != entry.status:
                repo.set_status(work_id, new)
                st.toast(f"Status updated: {STATUS_LABELS[new]}", icon="✅")
                st.rerun()
            if st.button("Remove from my library", key="remove"):
                repo.remove_from_library(work_id)
                st.toast("Book removed from your library", icon="🗑️")
                st.rerun()
    except BusinessRuleError as exc:
        st.warning(str(exc))
    except DataUnavailable:
        st.error("The server is not responding. Please try again in a moment.")

st.divider()
ui.html("<div class='shelf-title' style='margin-top:0'>Reviews</div>")

if entry and entry.status in RATING_STATUSES:
    with st.form(f"review_{work_id}", border=False):
        st.markdown("**My rating and review**")
        rating = st.feedback("stars", key=f"stars_{work_id}")
        mine = next((r for r in repo.book_reviews(work_id) if r.is_mine), None)
        text = st.text_area(
            "My review", value=mine.text if mine else "", placeholder="What did you think of this book?",
            label_visibility="collapsed",
        )
        if st.form_submit_button("Post", type="primary"):
            try:
                repo.save_review(work_id, None if rating is None else rating + 1, text)
                st.toast("Review saved", icon="✍️")
                st.rerun()
            except (BusinessRuleError, DataUnavailable) as exc:
                st.warning(str(exc))
elif entry:
    st.caption("You can rate this book and write a review once it is marked “Read” or “Did Not Finish”.")
else:
    st.caption("Add this book to your library to rate it after reading.")

reviews = ui.safe(lambda: repo.book_reviews(work_id), [])
for review in reviews:
    ui.review_card(review, repo, scope="book")
if not reviews and "reviews" in repo.supports:
    ui.empty("No reviews yet", "Be the first to share your opinion.")
elif not reviews:
    st.caption("Reviews will be shown as soon as the server provides them.")
