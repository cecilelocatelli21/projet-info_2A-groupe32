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
    ui.empty("Livre introuvable", "Reviens à l'accueil pour choisir un livre.")
    st.page_link(ui.PAGES["home"], label="← Retour à l'accueil")
    st.stop()

entry = ui.safe(lambda: repo.entry(work_id))
if st.button("← Retour", key="back"):
    st.switch_page(ui.PAGES["home"])

left, right = st.columns([1, 2.4], gap="large")
with left:
    ui.html(f"<div style='max-width:320px'>{ui.cover(book, entry, info=False)}</div>")

with right:
    chips = "".join(f"<span class='chip'>{escape(g)}</span>" for g in book.genres)
    ui.html(f"<div>{chips}</div><h1 class='book-title'>{escape(book.title)}</h1>")
    ui.html(f"<div class='hero-author'>{escape(book.authors_label)}</div>")
    ui.html(f"<div>{ui.stars(book.rating, book.ratings_count) or '<small style=color:var(--muted)>Pas encore de note</small>'}</div>")
    ui.html(
        f"<p style='color:#d9d3e0;line-height:1.65;max-width:720px;margin-top:1rem'>"
        f"{escape(book.description or 'Aucune description disponible pour ce livre.')}</p>"
    )
    facts = [
        ("Publication", book.published),
        ("Pages", book.pages),
        ("Éditeur", book.publisher),
        ("ISBN", book.isbn),
    ]
    cells = "".join(f"<div><span>{k}</span><b>{escape(str(v))}</b></div>" for k, v in facts if v)
    if cells:
        ui.html(f"<div class='meta-grid'>{cells}</div>")

    st.markdown("##### Ma lecture")
    try:
        if entry is None:
            c1, c2 = st.columns([1.2, 1.4])
            status = c2.selectbox(
                "Statut", STATUSES, format_func=STATUS_LABELS.get, label_visibility="collapsed", key="add_status"
            )
            if c1.button("＋  Ajouter à ma bibliothèque", type="primary", width="stretch"):
                if ui.add_book(repo, book, status):
                    st.rerun()
        else:
            ui.html(f"Statut actuel : {ui.status_chip(entry.status)}")
            new = st.segmented_control(
                "Changer le statut", STATUSES, default=entry.status, format_func=STATUS_LABELS.get,
                key=f"seg_{work_id}_{entry.status}",
            )
            if new and new != entry.status:
                repo.set_status(work_id, new)
                st.toast(f"Statut mis à jour : {STATUS_LABELS[new]}", icon="✅")
                st.rerun()
            if st.button("Retirer de ma bibliothèque", key="remove"):
                repo.remove_from_library(work_id)
                st.toast("Livre retiré de ta bibliothèque", icon="🗑️")
                st.rerun()
    except BusinessRuleError as exc:
        st.warning(str(exc))
    except DataUnavailable:
        st.error("Le serveur ne répond pas, réessaie dans un instant.")

st.divider()
ui.html("<div class='shelf-title' style='margin-top:0'>Critiques</div>")

if entry and entry.status in RATING_STATUSES:
    with st.form(f"review_{work_id}", border=False):
        st.markdown("**Ma note et ma critique**")
        rating = st.feedback("stars", key=f"stars_{work_id}")
        mine = next((r for r in repo.book_reviews(work_id) if r.is_mine), None)
        text = st.text_area(
            "Ma critique", value=mine.text if mine else "", placeholder="Qu'as-tu pensé de ce livre ?",
            label_visibility="collapsed",
        )
        if st.form_submit_button("Publier", type="primary"):
            try:
                repo.save_review(work_id, None if rating is None else rating + 1, text)
                st.toast("Critique enregistrée", icon="✍️")
                st.rerun()
            except (BusinessRuleError, DataUnavailable) as exc:
                st.warning(str(exc))
elif entry:
    st.caption("Tu pourras noter ce livre et écrire une critique une fois qu'il sera marqué « Lu » ou « Abandonné ».")
else:
    st.caption("Ajoute ce livre à ta bibliothèque pour pouvoir le noter après lecture.")

reviews = ui.safe(lambda: repo.book_reviews(work_id), [])
for review in reviews:
    ui.review_card(review, repo, scope="book")
if not reviews and "reviews" in repo.supports:
    ui.empty("Pas encore de critique", "Sois le premier à donner ton avis.")
elif not reviews:
    st.caption("L'affichage des critiques sera disponible dès que le serveur les proposera.")
