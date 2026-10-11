"""Home page: hero banner + Netflix-style shelves."""

import random

import streamlit as st

from data.factory import get_repository
from ui import components as ui

repo = get_repository()
ui.navbar("home")

with st.spinner("Chargement de ta sélection…"):
    featured = ui.safe(repo.featured, [])
    rows = ui.safe(repo.home_rows, [])

ui.source_banner(repo)

if featured:
    idx = st.session_state.setdefault("hero_idx", random.randrange(len(featured))) % len(featured)
    ui.hero(featured[idx], repo)
elif not rows:
    ui.empty("Rien à afficher pour l'instant", "Le catalogue est vide ou injoignable.")

for row in rows:
    ui.shelf(row.key, row.title, row.books, row.subtitle, repo)
