"""
Streamlit page showing a book: details, editions, average rating, reviews.

The page url is /book_details?work_id=OL45883W
The connected user can add the book to his library.

Endpoints used:
    GET /books/{work_id}
    GET /books/{work_id}/reviews
    POST /readings
"""

import pandas as pd
import streamlit as st

from api import books, readings
from utils.ui import READING_STATUSES, error_detail, init_page, show_api_error, status_label

logger = init_page("book_details", "Book", "📖")

work_id = st.query_params.get("work_id")
if not work_id:
    st.info("No book selected. Search a book first.")
    if st.button("Search books"):
        st.switch_page("pages/search_books.py")
    st.stop()

response = books.get_book(work_id)
if response["status_code"] == 404:
    st.error("Book not found.")
    st.stop()
if response["status_code"] != 200:
    show_api_error(response, logger, "load the book")
    st.stop()

book = response["data"]

col_cover, col_info = st.columns([1, 3])
with col_cover:
    if book.get("cover_url"):
        st.image(book["cover_url"], width=150)
    else:
        st.markdown("# 📕")
with col_info:
    st.subheader(book.get("title") or "Untitled")
    st.write(book.get("authors") or "Unknown author")
    average_rating = book.get("average_rating")
    st.metric("Average rating", f"{average_rating:.1f} / 5" if average_rating is not None else "—")

if book.get("description"):
    st.write(book["description"])

# --- Add to the library
st.subheader("Add to my library")
status = st.selectbox("Status", READING_STATUSES, format_func=status_label)
if st.button("Add to my library"):
    logger.info(f"Add book {work_id} to the library with status {status}")
    added = readings.add_reading(work_id, status)
    if added["status_code"] in (200, 201):
        st.success("Book added to your library 🎉")
    elif added["status_code"] == 409:
        st.info("This book is already in your library.")
    elif added["status_code"] == 404:
        st.error("This book could not be found on OpenLibrary.")
    else:
        show_api_error(added, logger, "add the book")

# --- Editions
editions = book.get("editions") or []
if editions:
    st.subheader("Editions")
    st.dataframe(pd.DataFrame(editions), hide_index=True)

# --- Reviews of the book (vertical Review: shown as soon as the backend provides them)
st.subheader("Reviews")
reviews_response = books.get_book_reviews(work_id)
if reviews_response["status_code"] == 200:
    reviews = reviews_response["data"]
    if not reviews:
        st.info("No review yet.")
    for review in reviews:
        with st.container(border=True):
            st.markdown(f"**{review['username']}** · {review['publication_date']}")
            st.write(review["text"])
            st.caption(f"👍 {review['likes']}  ·  👎 {review['dislikes']}")
else:
    logger.info(f"Reviews not available: {reviews_response['status_code']}")
    st.caption(f"Reviews are not available yet ({error_detail(reviews_response['data'])}).")

if st.button("Back to search", type="primary"):
    st.switch_page("pages/search_books.py")
