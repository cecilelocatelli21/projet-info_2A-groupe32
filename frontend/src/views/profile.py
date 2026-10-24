"""Profile page, reused for every user: ``/profile`` is mine, ``/profile?user=<id>`` is public.

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
    ui.empty("Profile not found", "This user does not exist or is no longer available.")
    if st.button("← Back to Home", key="profile_home"):
        st.switch_page(ui.PAGES["home"])
    st.stop()


def mine_or_theirs(mine: str, theirs: str) -> str:
    return mine if is_own else theirs


# ---- header ------------------------------------------------------------------------------------
since = f" · member since {profile.member_since:%m/%Y}" if profile.member_since else ""
bio = escape(profile.bio) if profile.bio else "<i style='color:var(--muted)'>No biography yet.</i>"
ui.html(
    f"<div class='profile-head'>{ui.avatar(profile.display_name)}"
    f"<div><h1>{escape(profile.display_name)}</h1>"
    f"<span style='color:var(--muted)'>@{escape(profile.username)}{since}</span><p>{bio}</p></div></div>"
)
ui.source_banner(repo)

if is_own and not st.session_state.get("mode") == "demo":
    st.space("xsmall")
    if st.button("✎  Edit profile", key="profile_edit"):
        st.switch_page(ui.PAGES["edit_profile"])

if not is_own and "follow" in repo.supports:
    try:
        following = repo.is_following(user_id)
        label = "Unfollow" if following else "＋ Follow"
        if st.button(label, key="follow_toggle", type="secondary" if following else "primary"):
            (repo.unfollow if following else repo.follow)(user_id)
            st.rerun()
    except BusinessRuleError as exc:
        st.warning(str(exc))
    except DataUnavailable:
        st.caption("Following is temporarily unavailable.")

# ---- data (one call per kind, reused by all sections) -----------------------------------------
loaded = ui.safe(lambda: repo.library(user_id=user_id), None)
library_ok = loaded is not None  # False when the request failed: no misleading "0"
entries = loaded or []
reviews = ui.safe(lambda: repo.user_reviews(user_id), [])
reviews_available = "reviews" in repo.supports

stats = [
    ("Books in library", len(entries) if library_ok else "—"),
    ("Books read", sum(e.status == "read" for e in entries) if library_ok else "—"),
    ("Currently reading", sum(e.status == "in progress" for e in entries) if library_ok else "—"),
    ("Reviews", len(reviews) if reviews_available else "—"),
    ("Followers", len(profile.followers)),
    ("Following", len(profile.following)),
]
st.space("small")
for col, (label, value) in zip(st.columns(len(stats)), stats, strict=True):
    col.markdown(f"<div class='stat'><b>{value}</b><span>{label}</span></div>", unsafe_allow_html=True)

# ---- library -----------------------------------------------------------------------------------
ui.html(f"<div class='shelf-title'>{mine_or_theirs('My Library', 'Library')}</div>")
if not library_ok:
    pass  # the error message has already been shown by ui.safe
elif not entries:
    ui.empty(
        mine_or_theirs("Your library is empty", "Empty library"),
        mine_or_theirs("Add books from Home.", "This user has not added any books yet."),
    )
else:
    done = sorted(
        (e for e in entries if e.status == "read"), key=lambda e: e.date_read or e.date_added, reverse=True
    )
    ui.shelf("latest", mine_or_theirs("My latest reads", "Latest reads"), [e.book for e in done[:12]], repo=repo)
    counts = {s: sum(e.status == s for e in entries) for s in STATUSES}
    tabs = st.tabs([f"{STATUS_LABELS[s]} · {counts[s]}" for s in STATUSES])
    for tab, status in zip(tabs, STATUSES, strict=True):
        with tab:
            items = [(e.book, None) for e in entries if e.status == status]
            if items:
                ui.grid(f"pl{status}".replace(" ", ""), items)
            else:
                st.caption("No books in this category.")

# ---- reviews, genres, community ----------------------------------------------------------------
left, right = st.columns([1.5, 1], gap="large")
with left:
    ui.html(f"<div class='shelf-title'>{mine_or_theirs('My reviews and ratings', 'Latest reviews')}</div>")
    if reviews:
        for review in reviews[:10]:
            book = ui.safe(lambda r=review: repo.get_book(r.work_id))
            ui.review_card(review, repo, scope="prof", book=book)
    elif not reviews_available:
        ui.empty("Reviews coming soon", "The server does not provide reviews yet.")
    else:
        ui.empty("No reviews yet", mine_or_theirs("Rate a book you have read to see it here.", "This user has not posted a review yet."))

with right:
    ui.html("<div class='shelf-title'>Top genres</div>")
    tally: dict[str, int] = {}
    for e in entries:
        for g in e.book.genres:
            tally[g] = tally.get(g, 0) + 1
    top = sorted(tally.items(), key=lambda kv: -kv[1])[:5]
    if top:
        st.caption("Estimated from the books in the library, not from declared preferences.")
        for genre, n in top:
            ui.html(
                f"<div class='bar-l'><span>{escape(genre)}</span><span>{n}</span></div>"
                f"<div class='bar'><i style='width:{100 * n // top[0][1]}%'></i></div>"
            )
    else:
        st.caption("Genres are not available for these books.")

    ui.html("<div class='shelf-title'>Community</div>")
    if "social" in repo.supports:
        t1, t2 = st.tabs([f"Followers · {len(profile.followers)}", f"Following · {len(profile.following)}"])
        for tab, people, key in ((t1, profile.followers, "fw"), (t2, profile.following, "fg")):
            with tab:
                if not people:
                    st.caption("Nobody yet.")
                for p in people:
                    ui.person_row(p, key)
