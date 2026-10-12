"""Profile page, reused for every user: ``/profil`` is mine, ``/profil?user=<id>`` is public.

Any connected user can open any profile (library, readings and reviews are public); following
someone only changes the Follow button, never what can be seen.
"""

from html import escape

import streamlit as st

from data.errors import BusinessRuleError, DataUnavailable
from data.factory import get_repository
from data.models import STATUS_LABELS, STATUSES
from ui import components as ui

repo = get_repository()
ui.navbar("profile")

# ---- which user? -------------------------------------------------------------------------------
raw_id = st.query_params.get("user")
try:
    requested = None if raw_id is None else int(raw_id)
except ValueError:
    requested = -1  # not a number: shown as an unknown profile
is_own = requested is None or requested == repo.own_id
user_id = repo.own_id if is_own else requested

profile = ui.safe(lambda: repo.profile(user_id)) if requested != -1 else None
if profile is None:
    ui.empty("Profil introuvable", "Cet utilisateur n'existe pas ou n'est plus disponible.")
    if st.button("← Retour à l'accueil", key="profile_home"):
        st.switch_page(ui.PAGES["home"])
    st.stop()


def mine_or_theirs(mine: str, theirs: str) -> str:
    return mine if is_own else theirs


# ---- header ------------------------------------------------------------------------------------
since = f" · membre depuis {profile.member_since:%m/%Y}" if profile.member_since else ""
bio = escape(profile.bio) if profile.bio else "<i style='color:var(--muted)'>Pas encore de biographie.</i>"
ui.html(
    f"<div class='profile-head'>{ui.avatar(profile.display_name)}"
    f"<div><h1>{escape(profile.display_name)}</h1>"
    f"<span style='color:var(--muted)'>@{escape(profile.username)}{since}</span><p>{bio}</p></div></div>"
)
ui.source_banner(repo)

if not is_own and "follow" in repo.supports:
    try:
        following = repo.is_following(user_id)
        label = "Ne plus suivre" if following else "＋ Suivre"
        if st.button(label, key="follow_toggle", type="secondary" if following else "primary"):
            (repo.unfollow if following else repo.follow)(user_id)
            st.rerun()
    except BusinessRuleError as exc:
        st.warning(str(exc))
    except DataUnavailable:
        st.caption("Le suivi est momentanément indisponible.")

# ---- data (one call per kind, reused by all sections) -----------------------------------------
loaded = ui.safe(lambda: repo.library(user_id=user_id), None)
library_ok = loaded is not None  # False when the request failed: no misleading "0"
entries = loaded or []
reviews = ui.safe(lambda: repo.user_reviews(user_id), [])
reviews_available = "reviews" in repo.supports

stats = [
    ("Livres dans la bibliothèque", len(entries) if library_ok else "—"),
    ("Livres lus", sum(e.status == "read" for e in entries) if library_ok else "—"),
    ("En cours de lecture", sum(e.status == "in progress" for e in entries) if library_ok else "—"),
    ("Critiques", len(reviews) if reviews_available else "—"),
    ("Abonnés", len(profile.followers)),
    ("Abonnements", len(profile.following)),
]
st.space("small")
for col, (label, value) in zip(st.columns(len(stats)), stats, strict=True):
    col.markdown(f"<div class='stat'><b>{value}</b><span>{label}</span></div>", unsafe_allow_html=True)

# ---- library -----------------------------------------------------------------------------------
ui.html(f"<div class='shelf-title'>{mine_or_theirs('Ma bibliothèque', 'Sa bibliothèque')}</div>")
if not library_ok:
    pass  # the error message has already been shown by ui.safe
elif not entries:
    ui.empty(
        mine_or_theirs("Ta bibliothèque est vide", "Bibliothèque vide"),
        mine_or_theirs("Ajoute des livres depuis l'accueil.", "Cet utilisateur n'a pas encore ajouté de livre."),
    )
else:
    done = sorted(
        (e for e in entries if e.status == "read"), key=lambda e: e.date_read or e.date_added, reverse=True
    )
    ui.shelf("latest", mine_or_theirs("Mes dernières lectures", "Dernières lectures"), [e.book for e in done[:12]], repo=repo)
    counts = {s: sum(e.status == s for e in entries) for s in STATUSES}
    tabs = st.tabs([f"{STATUS_LABELS[s]} · {counts[s]}" for s in STATUSES])
    for tab, status in zip(tabs, STATUSES, strict=True):
        with tab:
            items = [(e.book, None) for e in entries if e.status == status]
            if items:
                ui.grid(f"pl{status}".replace(" ", ""), items)
            else:
                st.caption("Aucun livre dans cette catégorie.")

# ---- reviews, genres, community ----------------------------------------------------------------
left, right = st.columns([1.5, 1], gap="large")
with left:
    ui.html(f"<div class='shelf-title'>{mine_or_theirs('Mes critiques et mes notes', 'Ses dernières critiques')}</div>")
    if reviews:
        for review in reviews[:10]:
            book = ui.safe(lambda r=review: repo.get_book(r.work_id))
            ui.review_card(review, repo, scope="prof", book=book)
    elif not reviews_available:
        ui.empty("Critiques bientôt disponibles", "Le serveur ne fournit pas encore les critiques.")
    else:
        ui.empty("Pas encore de critique", mine_or_theirs("Note un livre lu pour la voir ici.", "Cet utilisateur n'a pas encore publié de critique."))

with right:
    ui.html("<div class='shelf-title'>Genres les plus représentés</div>")
    tally: dict[str, int] = {}
    for e in entries:
        for g in e.book.genres:
            tally[g] = tally.get(g, 0) + 1
    top = sorted(tally.items(), key=lambda kv: -kv[1])[:5]
    if top:
        st.caption("Estimation d'après les livres de sa bibliothèque, pas des préférences déclarées.")
        for genre, n in top:
            ui.html(
                f"<div class='bar-l'><span>{escape(genre)}</span><span>{n}</span></div>"
                f"<div class='bar'><i style='width:{100 * n // top[0][1]}%'></i></div>"
            )
    else:
        st.caption("Les genres ne sont pas disponibles pour ces livres.")

    ui.html("<div class='shelf-title'>Communauté</div>")
    if "social" in repo.supports:
        t1, t2 = st.tabs([f"Abonnés · {len(profile.followers)}", f"Abonnements · {len(profile.following)}"])
        for tab, people, key in ((t1, profile.followers, "fw"), (t2, profile.following, "fg")):
            with tab:
                if not people:
                    st.caption("Personne pour l'instant.")
                for p in people:
                    ui.person_row(p, key)
