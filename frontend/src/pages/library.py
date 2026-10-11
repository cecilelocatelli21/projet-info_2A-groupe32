"""
Streamlit page showing the library of a user.

The page url is /library (own library) or /library?user_id=4 (library of someone else).
The owner can change the status, rate or remove a book; other users only read it.

Endpoints used:
    GET /users/{user_id}
    GET /users/{user_id}/readings?status=
    PATCH /readings/{reading_id}
    DELETE /readings/{reading_id}
"""

import pandas as pd
import streamlit as st

from api import readings, users
from utils.session import get_current_user
from utils.ui import (
    RATEABLE_STATUSES,
    READING_STATUSES,
    error_detail,
    flash,
    init_page,
    parse_id,
    show_api_error,
    status_label,
)

me = get_current_user() or {}
user_id = parse_id(st.query_params.get("user_id")) or me.get("user_id")
is_me = user_id == me.get("user_id")

logger = init_page("library", "My library" if is_me else "Library", "📚", layout="wide")

if not is_me:
    owner = users.get_user(user_id)
    if owner["status_code"] == 404:
        st.error("User not found.")
        st.stop()
    if owner["status_code"] != 200:
        show_api_error(owner, logger, "load the user")
        st.stop()
    st.subheader(f"{owner['data']['username']}'s library")

chosen = st.selectbox("Filter by status", ["all", *READING_STATUSES], format_func=status_label)
status_filter = None if chosen == "all" else chosen

response = readings.get_library(user_id, status_filter)
if response["status_code"] != 200:
    show_api_error(response, logger, "load the library")
    st.stop()

library = response["data"]
if not library:
    st.info("No book here yet." if status_filter is None else "No book with this status.")
else:
    st.dataframe(
        pd.DataFrame(
            {
                "Title": [r["book"]["title"] for r in library],
                "Authors": [r["book"]["authors"] for r in library],
                "Status": [status_label(r["status"]) for r in library],
                "Rating": [r["rating"] for r in library],
                "Added": [r["date_added"] for r in library],
                "Read": [r["date_read"] for r in library],
            }
        ),
        hide_index=True,
    )

# --- Management of the readings: only for the owner
if is_me:
    for reading in library:
        reading_id = reading["reading_id"]
        title = reading["book"]["title"] or "Untitled"
        with st.expander(f"Manage: {title}"):
            new_status = st.selectbox(
                "Status",
                READING_STATUSES,
                index=READING_STATUSES.index(reading["status"]),
                format_func=status_label,
                key=f"status_{reading_id}",
            )
            can_rate = new_status in RATEABLE_STATUSES
            current_rating = reading["rating"] or 0
            new_rating = st.slider(
                "Rating (only once the book is read or abandoned)",
                0,
                5,
                value=current_rating,
                disabled=not can_rate,
                key=f"rating_{reading_id}",
            )

            col_save, col_delete = st.columns(2)
            if col_save.button("Save", key=f"save_{reading_id}"):
                changes = {}
                if new_status != reading["status"]:
                    changes["status"] = new_status
                if can_rate and new_rating != current_rating:
                    changes["rating"] = new_rating
                if not changes:
                    st.info("Nothing to save.")
                else:
                    logger.info(f"Update reading {reading_id}: {changes}")
                    updated = readings.update_reading(reading_id, **changes)
                    if updated["status_code"] == 200:
                        flash("success", f"“{title}” updated ✅")
                        st.rerun()
                    elif updated["status_code"] in (400, 403, 404):
                        st.error(error_detail(updated["data"]))
                    else:
                        show_api_error(updated, logger, "update the reading")

            if col_delete.button("Remove from library", key=f"delete_{reading_id}"):
                logger.info(f"Delete reading {reading_id}")
                deleted = readings.delete_reading(reading_id)
                if deleted["status_code"] in (200, 204):
                    flash("success", f"“{title}” removed from your library")
                    st.rerun()
                elif deleted["status_code"] in (403, 404):
                    st.error(error_detail(deleted["data"]))
                else:
                    show_api_error(deleted, logger, "remove the reading")

if st.button("Back to menu", type="primary"):
    st.switch_page("pages/main_menu.py")
