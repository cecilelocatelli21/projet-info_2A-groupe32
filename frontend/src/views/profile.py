"""User profile: identity, stats, latest reads, reviews, favourite genres, social."""

from html import escape

import streamlit as st

from data.factory import get_repository
from ui import components as ui

repo = get_repository()
ui.navbar("profile")

profile = ui.safe(repo.profile)
entries = ui.safe(repo.library, [])
if profile is None:
    st.stop()

since = f" · membre depuis {profile.member_since:%m/%Y}" if profile.member_since else ""
bio = f"<p>{escape(profile.bio)}</p>" if profile.bio else ""
ui.html(
    f"<div class='profile-head'><div class='avatar'>{escape(profile.display_name[:1].upper())}</div>"
    f"<div><h1>{escape(profile.display_name)}</h1>"
    f"<span style='color:var(--muted)'>@{escape(profile.username)}{since}</span>{bio}</div></div>"
)
ui.source_banner(repo)

reviews = ui.safe(repo.my_reviews, [])
stats = [
    ("Dans ma bibliothèque", len(entries)),
    ("Livres lus", sum(e.status == "read" for e in entries)),
    ("En cours", sum(e.status == "in progress" for e in entries)),
    ("Critiques", len(reviews)),
    ("Abonnés", len(profile.followers)),
    ("Abonnements", len(profile.following)),
]
st.space("small")
for col, (label, value) in zip(st.columns(len(stats)), stats, strict=True):
    col.markdown(f"<div class='stat'><b>{value}</b><span>{label}</span></div>", unsafe_allow_html=True)

done = sorted((e for e in entries if e.status == "read"), key=lambda e: e.date_read or e.date_added, reverse=True)
ui.shelf("latest", "Mes dernières lectures", [e.book for e in done[:12]], repo=repo)

left, right = st.columns([1.5, 1], gap="large")
with left:
    ui.html("<div class='shelf-title'>Mes critiques et mes notes</div>")
    if reviews:
        for review in reviews:
            ui.review_card(review)
    else:
        rated = [e for e in entries if e.rating]
        if rated:
            for e in rated:
                ui.html(f"<div class='panel'><b>{escape(e.book.title)}</b> <span class='stars'>{'★' * e.rating}</span></div>")
        else:
            ui.empty("Pas encore de critique", "Note un livre lu depuis sa fiche pour le voir ici.")
with right:
    ui.html("<div class='shelf-title'>Genres préférés</div>")
    tally: dict[str, int] = {}
    for e in entries:
        for g in e.book.genres:
            tally[g] = tally.get(g, 0) + 1
    top = sorted(tally.items(), key=lambda kv: -kv[1])[:5]
    for genre, n in top:
        ui.html(
            f"<div class='bar-l'><span>{escape(genre)}</span><span>{n}</span></div>"
            f"<div class='bar'><i style='width:{100 * n // top[0][1]}%'></i></div>"
        )
    if not top:
        ui.empty("Pas encore de genres", "Ils apparaîtront avec tes lectures.")

    ui.html("<div class='shelf-title'>Communauté</div>")
    if "social" in repo.supports:
        t1, t2 = st.tabs([f"Abonnés · {len(profile.followers)}", f"Abonnements · {len(profile.following)}"])
        for tab, people in ((t1, profile.followers), (t2, profile.following)):
            with tab:
                if not people:
                    st.caption("Personne pour l'instant.")
                for p in people:
                    ui.html(
                        f"<div class='person'><div class='avatar sm'>{escape(p.username[:1].upper())}</div>"
                        f"<div><b>@{escape(p.username)}</b><span>{escape(p.bio or '')}</span></div></div>"
                    )
