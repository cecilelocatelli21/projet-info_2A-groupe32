"""Discover & search: text search (navbar), genre/author filters, sorting, cover grid."""

import streamlit as st

from data.factory import get_repository
from data.search import SORT_LABELS
from ui import components as ui

repo = get_repository()
ui.navbar("discover")
ui.page_header("Découvrir", "Cherche un titre, un auteur, ou explore par genre.")

query = st.session_state.get("search_q", "")
c1, c2, c3 = st.columns([2, 2, 1.2])
genres = c1.multiselect("Genres", ui.safe(repo.genres, []), placeholder="Tous les genres")
authors = c2.multiselect("Auteurs", ui.safe(repo.authors, []), placeholder="Tous les auteurs")
sort = c3.selectbox("Trier par", list(SORT_LABELS), format_func=SORT_LABELS.get)

results = ui.safe(lambda: repo.search(query, genres, authors, sort), [])
ui.source_banner(repo)
label = f"« {query} » — " if query else ""
st.caption(f"{label}{len(results)} livre{'s' if len(results) > 1 else ''}")

if results:
    ui.grid("disc", [(b, repo.entry(b.work_id) if repo.source == "demo" else None) for b in results])
else:
    ui.empty("Aucun livre trouvé", "Essaie un autre titre, ou retire un filtre.")
    if query:
        st.button("Effacer la recherche", on_click=ui.clear_search)
