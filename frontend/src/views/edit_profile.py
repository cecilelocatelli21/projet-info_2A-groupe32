"""Edit Profile: bio and e-mail, password, and (in its own section) account deletion.

Backend routes (all need the Bearer token and only work on the connected user's own account):
    GET    /users/me                  current bio and e-mail (the private view of one's own account)
    PUT    /users/{id}                bio and/or e-mail; a field that is not sent is left unchanged
    PUT    /users/{id}/password       {old_password, new_password}; the old password is checked
    DELETE /users/{id}                account deletion; readings, reviews, likes and follows go with it
                                      (ON DELETE CASCADE in data/init_db.sql)

``PUT``/``DELETE /player/{id_player}`` are not used: they edit the former template ``player`` table
(elo, pokemon_fan...), have no bio and no authentication. The id always comes from the session.
"""

import os
import re

import streamlit as st

from api import users as users_api
from auth import session
from ui import components as ui
from ui.components import html

BIO_MAX = 1000  # schema/user_model.py: BIO_MAX_LENGTH
PASSWORD_MIN = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))  # same variable as the backend
PASSWORD_MAX = 128
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

ui.navbar("edit_profile")

if session.is_demo():
    ui.page_header("Edit Profile", "")
    st.info("Profile editing is not available in demo mode: the demo account is fictitious.")
    st.stop()

ui.page_header("Edit Profile", "Update your public biography, your e-mail address and your password.")
if st.button("← Back to my profile", key="back_profile"):
    st.switch_page(ui.PAGES["profile"])

flash = st.session_state.pop("profile_flash", None)
if flash:
    st.success(flash)

# ---- current values (own private view, GET /users/me) ----------------------------------------------
me = users_api.get_me()
if me["status_code"] == 401:
    session.expire()
    st.rerun()
if me["status_code"] != 200 or not isinstance(me["data"], dict):
    if me["status_code"] == 404:
        session.expire("This account no longer exists.")
        st.rerun()
    st.error(
        "The server is unreachable right now. Please try again in a moment."
        if me["status_code"] == 0
        else "Your profile could not be loaded. Please try again later."
    )
    st.stop()
current_bio = me["data"].get("bio") or ""
current_email = me["data"].get("email") or ""

# ---- profile ---------------------------------------------------------------------------------------
with st.container(key="edit_card_profile"):
    html("<h3>Profile</h3>")
    with st.form("edit_profile_form", border=False):
        html(f"<div class='page-sub'>Username: <b>@{ui.escape(session.display_name())}</b> (it cannot be changed)</div>")
        bio = st.text_area("Biography", value=current_bio, max_chars=BIO_MAX, height=140,
                           placeholder="Tell other readers a few words about you…")
        email = st.text_input("Email", value=current_email, autocomplete="email")
        saved = st.form_submit_button("Save changes", type="primary")
    if saved:
        email = email.strip()
        if email and not EMAIL_RE.match(email):
            st.error("Please enter a valid email address.")
        elif not email:
            st.error("Your email address cannot be empty.")
        else:
            # PUT /users/{id}: only what changed is sent, the rest stays as it is on the server
            changes = {}
            if bio != current_bio:
                changes["bio"] = bio
            if email != current_email:
                changes["email"] = email
            if not changes:
                st.info("Nothing to save: you have not changed anything.")
            else:
                with st.spinner("Saving…"):
                    error = session.api_update_profile(**changes)
                if error:
                    st.error(error)
                    if not session.is_logged_in():
                        st.rerun()
                else:
                    st.session_state["profile_flash"] = "Your profile has been updated."
                    st.rerun()  # reloads the values from the server

# ---- password --------------------------------------------------------------------------------------
with st.container(key="edit_card_password"):
    html("<h3>Password</h3>")
    with st.form("edit_password_form", border=False, clear_on_submit=True):
        old = st.text_input("Current password", type="password", autocomplete="current-password")
        new = st.text_input("New password", type="password", autocomplete="new-password",
                            placeholder=f"at least {PASSWORD_MIN} characters")
        confirm = st.text_input("Confirm new password", type="password", autocomplete="new-password")
        changed = st.form_submit_button("Change password", type="primary")
    if changed:
        if not old:
            st.error("Please enter your current password.")
        elif len(new) < PASSWORD_MIN:
            st.error(f"Your new password must be at least {PASSWORD_MIN} characters long.")
        elif len(new) > PASSWORD_MAX:
            st.error(f"Your new password must be at most {PASSWORD_MAX} characters long.")
        elif new != confirm:
            st.error("The two new passwords do not match.")
        elif new == old:
            st.error("Your new password must be different from the current one.")
        else:
            with st.spinner("Changing your password…"):
                error = session.api_change_password(old, new)
            if error:
                st.error(error)
                if not session.is_logged_in():
                    st.rerun()
            else:
                st.success("Your password has been changed. Use it the next time you log in.")

# ---- delete account --------------------------------------------------------------------------------
with st.container(key="edit_card_delete"):
    html("<h3>Delete Account</h3>")
    html(
        "<div class='page-sub'>Permanently delete your Ex-Libris account. Your library, ratings, reviews, "
        "likes and the people you follow are deleted with it. This cannot be undone.</div>"
    )


@st.dialog("Delete your account?")
def confirm_delete() -> None:
    st.markdown(
        f"You are about to permanently delete the account **@{session.display_name()}**.\n\n"
        "Your library, your ratings and reviews, your likes and your follows will be deleted too. "
        "**This cannot be undone.**"
    )
    c1, c2 = st.columns(2)
    if c1.button("Cancel", key="delete_cancel", width="stretch"):
        st.rerun()
    if c2.button("Yes, delete my account", key="delete_confirm", type="primary", width="stretch"):
        with st.spinner("Deleting your account…"):
            error = session.api_delete_account()
        if error:
            st.error(error)
            if not session.is_logged_in():
                st.rerun()
        else:
            st.rerun()  # the session is gone: the public home page opens with a confirmation


with st.container(key="edit_delete_action"):
    if st.button("Delete Account", key="delete_open", type="primary"):
        confirm_delete()
