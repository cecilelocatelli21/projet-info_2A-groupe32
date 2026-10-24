"""Book detail page: Open Library details, library actions, rating & review, other readers' reviews.

The details come from ``GET /books/{work_id}`` (token required, the backend asks Open Library): title,
authors, ``cover_url``, ``subjects`` (shown as small labels), ``description``, ``editions`` and the
``average_rating`` of Ex-Libris readers. Only fields really present in the answer are displayed.
If the details cannot be obtained, the page still shows the book as it was listed and says so.
"""

from html import escape

import streamlit as st

from data.errors import BusinessRuleError, DataUnavailable
from data.factory import get_repository
from data.models import RATING_STATUSES, STATUS_LABELS, STATUSES
from ui import components as ui

repo = get_repository()
ui.navbar("book")

work_id = st.session_state.get("selected_work")
with st.spinner("Loading book details…"):
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

SUBJECTS_SHOWN = 8
with right:
    shown, hidden = book.genres[:SUBJECTS_SHOWN], book.genres[SUBJECTS_SHOWN:]
    chips = "".join(f"<span class='chip'>{escape(g)}</span>" for g in shown)
    if hidden:
        chips += f"<span class='chip chip-more'>+{len(hidden)} more</span>"
    ui.html(f"<div>{chips}</div><h1 class='book-title'>{escape(book.title)}</h1>")
    ui.html(f"<div class='hero-author'>{escape(book.authors_label)}</div>")
    if book.rating:
        ui.html(f"<div>{ui.stars(book.rating, book.ratings_count)} <small style='color:var(--muted)'>average rating of Ex-Libris readers</small></div>")
    if repo.source == "api" and not book.detailed:
        st.caption("Details from Open Library are temporarily unavailable: only the basic information is shown.")
    if book.description:
        ui.html(f"<p class='book-desc'>{escape(book.description)}</p>")
    elif book.detailed:
        ui.html("<p class='book-desc muted'>No description available for this book.</p>")
    facts = [
        ("Published", book.published),
        ("Pages", book.pages),
        ("Publisher", book.publisher),
        ("ISBN", book.isbn),
    ]
    cells = "".join(f"<div><span>{k}</span><b>{escape(str(v))}</b></div>" for k, v in facts if v)
    if cells:
        ui.html(f"<div class='meta-grid'>{cells}</div>")
    if hidden:
        with st.expander(f"All subjects ({len(book.genres)})"):
            ui.html("".join(f"<span class='chip'>{escape(g)}</span>" for g in book.genres))
    if book.editions:
        with st.expander(f"Editions ({len(book.editions)})"):
            for ed in book.editions:
                details = [
                    ed.publisher,
                    ed.publish_date,
                    f"{ed.pages} pages" if ed.pages else None,
                    f"ISBN {ed.isbn}" if ed.isbn else None,
                ]
                line = " · ".join(escape(str(d)) for d in details if d)
                title = f"<b>{escape(ed.title)}</b>" if ed.title else "<b>Edition</b>"
                ui.html(f"<div class='edition'>{title}{f'<span>{line}</span>' if line else ''}</div>")

    with st.container(key="reading_panel"):
        ui.html("<div class='panel-title'>My reading</div>")
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
                seg_key = f"seg_{work_id}_{entry.status}"
                new = st.segmented_control(
                    "Change status", STATUSES, default=entry.status, format_func=STATUS_LABELS.get, key=seg_key
                )
                if new and new != entry.status:
                    try:
                        with st.spinner("Updating…"):
                            repo.set_status(work_id, new)
                    except (BusinessRuleError, DataUnavailable) as exc:
                        st.session_state.pop(seg_key, None)  # the selector goes back to the saved status
                        st.toast(str(exc) if isinstance(exc, BusinessRuleError) else "The server is not responding.", icon="⚠️")
                        st.rerun()
                    st.toast(f"Status updated: {STATUS_LABELS[new]}", icon="✅")
                    st.rerun()
                if st.button("Remove from my library", key="remove", type="tertiary"):
                    repo.remove_from_library(work_id)
                    st.toast("Book removed from your library", icon="🗑️")
                    st.rerun()
        except BusinessRuleError as exc:
            st.warning(str(exc))
        except DataUnavailable:
            st.error("The server is not responding. Please try again in a moment.")

st.divider()
reviews = ui.safe(lambda: repo.book_reviews(work_id), [])
mine = next((r for r in reviews if r.is_mine), None)
others = [r for r in reviews if not r.is_mine]
ui.html(f"<div class='shelf-title' style='margin-top:0'>Reviews <span class='count'>{len(reviews)}</span></div>")

if entry and entry.status in RATING_STATUSES and mine is None:
    # no review yet: rate and/or write one. Once it exists it is edited in place ("Edit review"), never rewritten here.
    with st.container(key="review_form"):
        with st.form(f"review_{work_id}", border=False):
            st.markdown("**Rate this book and share your thoughts**")
            rating = st.feedback("stars", key=f"stars_{work_id}", default=(entry.rating - 1) if entry.rating else None)
            text = st.text_area(
                "My review", placeholder="What did you think of this book?", label_visibility="collapsed", height=120, max_chars=2000
            )
            if st.form_submit_button("Post review", type="primary"):
                try:
                    with st.spinner("Saving…"):
                        repo.save_review(work_id, None if rating is None else rating + 1, text)
                    st.toast("Review saved", icon="✍️")
                    st.rerun()
                except (BusinessRuleError, DataUnavailable) as exc:
                    st.warning(str(exc))
elif entry and mine is None:
    st.caption("You can rate this book and write a review once it is marked “read” or “abandoned”.")
elif not entry:
    st.caption("Add this book to your library to rate it after reading.")

for review in ([mine] if mine else []) + others:
    ui.review_card(review, repo, scope="book")
if not reviews and "reviews" in repo.supports:
    ui.empty("No reviews yet", "Be the first to share your opinion.")
elif not reviews:
    st.caption("Reviews will be shown as soon as the server provides them.")
