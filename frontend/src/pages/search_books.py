"""
Streamlit page for searching books on OpenLibrary.

Each result links to the book page, where it can be added to the library.

Endpoint used:
    GET /books?q=
"""

import streamlit as st

from api import books
from utils.ui import init_page, render_book, show_api_error

logger = init_page("search_books", "Search books", "🔎")

with st.form("search_books_form"):
    query = st.text_input(
        "Title or author", value=st.session_state.get("book_query", ""), placeholder="Dune"
    )
    submitted = st.form_submit_button("Search")

if submitted and query.strip():
    logger.info(f"Search books: {query}")
    with st.spinner("Searching OpenLibrary..."):
        response = books.search_books(query.strip())
    if response["status_code"] == 200:
        # Kept in session_state so the results survive the next reruns
        st.session_state["book_query"] = query.strip()
        st.session_state["book_results"] = response["data"]
    else:
        st.session_state.pop("book_results", None)
        show_api_error(response, logger, "search books")

results = st.session_state.get("book_results")
if results is not None:
    if results:
        st.caption(f"{len(results)} result(s) for “{st.session_state.get('book_query', '')}”")
        for book in results:
            render_book(book)
    else:
        st.info("No book found.")

if st.button("Back to menu", type="primary"):
    st.switch_page("pages/main_menu.py")
