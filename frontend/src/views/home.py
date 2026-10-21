"""Home page (logged in): hero banner + Netflix-style shelves."""

import random

import streamlit as st

from data.factory import get_repository
from ui import components as ui

repo = get_repository()
ui.navbar("home")

with st.spinner("Loading your selection…"):
    featured = ui.safe(repo.featured, [])
    rows = ui.safe(repo.home_rows, [])

ui.source_banner(repo)

if featured:
    idx = st.session_state.setdefault("hero_idx", random.randrange(len(featured))) % len(featured)
    ui.hero(featured[idx], repo)
elif not rows:
    ui.empty("Nothing to show yet", "The catalogue is empty or unreachable.")

for row in rows:
    ui.shelf(row.key, row.title, row.books, row.subtitle, repo)
