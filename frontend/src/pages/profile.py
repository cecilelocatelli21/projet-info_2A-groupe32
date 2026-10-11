"""
Streamlit page showing the profile of a user.

The page url is /profile (own profile) or /profile?user_id=4 (someone else's profile).
Shows the public data, the follower and following lists, and lets the connected user
follow or unfollow the person.

Endpoints used:
    GET /users/me
    GET /users/{user_id}
    GET /users/{user_id}/following
    GET /users/{user_id}/followers
    POST /users/{user_id}/follow
    DELETE /users/{user_id}/follow
"""

import streamlit as st

from api import follows, users
from utils.session import get_current_user
from utils.ui import error_detail, flash, init_page, parse_id, render_user, show_api_error

me = get_current_user() or {}
user_id = parse_id(st.query_params.get("user_id")) or me.get("user_id")
is_me = user_id == me.get("user_id")

logger = init_page("profile", "My profile" if is_me else "Profile", "👤")

response = users.get_me() if is_me else users.get_user(user_id)
if response["status_code"] == 404:
    st.error("User not found.")
    st.stop()
if response["status_code"] != 200:
    show_api_error(response, logger, "load the profile")
    st.stop()

profile = response["data"]
st.subheader(profile["username"])
st.write(profile.get("bio") or "_No bio yet_")
if is_me and profile.get("email"):
    st.caption(f"✉️ {profile['email']}")


def load_users(call, action: str) -> list[dict]:
    """Calls follows.get_following / get_followers, an empty list if it fails."""
    result = call(user_id)
    if result["status_code"] == 200:
        return result["data"]
    show_api_error(result, logger, action)
    return []


following = load_users(follows.get_following, "load the following list")
followers = load_users(follows.get_followers, "load the followers list")

col_followers, col_following = st.columns(2)
col_followers.metric("Followers", len(followers))
col_following.metric("Following", len(following))

# --- Follow / unfollow (not on his own profile)
if not is_me:
    i_follow = any(u["user_id"] == me["user_id"] for u in followers)
    if i_follow:
        if st.button("Unfollow"):
            logger.info(f"Unfollow user {user_id}")
            result = follows.unfollow(user_id)
            if result["status_code"] in (200, 204):
                flash("success", f"You no longer follow {profile['username']}.")
                st.rerun()
            elif result["status_code"] == 404:
                st.error(error_detail(result["data"]))
            else:
                show_api_error(result, logger, "unfollow")
    else:
        if st.button("Follow", type="primary"):
            logger.info(f"Follow user {user_id}")
            result = follows.follow(user_id)
            if result["status_code"] in (200, 201):
                flash("success", f"You now follow {profile['username']} 🎉")
                st.rerun()
            elif result["status_code"] in (400, 404, 409):
                st.error(error_detail(result["data"]))
            else:
                show_api_error(result, logger, "follow")

st.page_link(
    "pages/library.py",
    label="My library" if is_me else "Library",
    icon="📚",
    query_params={"user_id": user_id},
)

tab_followers, tab_following = st.tabs(
    [f"Followers ({len(followers)})", f"Following ({len(following)})"]
)
with tab_followers:
    if followers:
        for follower in followers:
            render_user(follower)
    else:
        st.info("No follower yet.")
with tab_following:
    if following:
        for followed in following:
            render_user(followed)
    else:
        st.info("Not following anyone yet.")

if st.button("Back to menu", type="primary"):
    st.switch_page("pages/main_menu.py")
