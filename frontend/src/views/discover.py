"""Discover & search: text search (navbar), genre/author filters, sorting, cover grid."""

import streamlit as st

from data.errors import DataUnavailable
from data.factory import get_repository
from data.search import SORT_LABELS
from ui import components as ui

repo = get_repository()
ui.navbar("discover")
ui.page_header("Découvrir", "Cherche un titre, un auteur, ou explore par genre.")

query = st.session_state.get("search_q", "").strip()
remote = repo.source == "api" and bool(query)  # keyword search = GET /books?q=...
failure = None  # set when the backend cannot answer: shown once, never mistaken for "no result"

found = []
if remote:
    with st.spinner("Recherche en cours…"):
        try:
            found = repo.search(query)
        except DataUnavailable as exc:
            failure = exc

c1, c2, c3 = st.columns([2, 2, 1.2])
if remote:
    # OpenLibrary results carry no genre: only the authors found are offered as a filter
    genres = []
    c1.multiselect("Genres", [], placeholder="Genres : non fournis par la recherche", disabled=True)
    author_options = sorted({a for b in found for a in b.authors})
else:
    genres = c1.multiselect("Genres", ui.safe(repo.genres, []), placeholder="Tous les genres")
    author_options = ui.safe(repo.authors, [])
authors = c2.multiselect("Auteurs", author_options, placeholder="Tous les auteurs")
sort = c3.selectbox("Trier par", list(SORT_LABELS), format_func=SORT_LABELS.get)

results = []
if failure is None:
    with st.spinner("Chargement…"):
        try:
            results = repo.search(query, genres, authors, sort)
        except DataUnavailable as exc:
            failure = exc
ui.source_banner(repo)

if failure is not None:
    ui.empty("Recherche indisponible", "Le serveur ne répond pas pour le moment. Réessaie dans un instant.")
    st.caption(f"Détail technique : {failure}")
    st.button("Réessayer")
elif results:
    st.caption(f"{'« ' + query + ' » — ' if query else ''}{len(results)} livre{'s' if len(results) > 1 else ''}")
    ui.grid("disc", [(b, repo.entry(b.work_id) if repo.source == "demo" else None) for b in results])
else:
    st.caption(f"« {query} » — 0 livre" if query else "")
    ui.empty("Aucun livre trouvé", "Essaie un autre titre ou un autre mot-clé, ou retire un filtre." if query else "Le catalogue est vide pour le moment.")
    if query:
        st.button("Effacer la recherche", on_click=ui.clear_search)
