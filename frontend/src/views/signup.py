"""Account creation page: real ``POST /user/users`` (username, email, password).

The backend does not log the new user in (no token in the answer), so after a successful creation the
visitor is sent to the login page with a confirmation message.
"""

import os
import re

import streamlit as st

from auth import session
from ui import components as ui
from ui.components import html

USERNAME_MIN, USERNAME_MAX = 2, 30  # schema/user_model.py: UserModel.username
PASSWORD_MAX = 128
PASSWORD_MIN = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))  # same variable as the backend
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate(username: str, email: str, password: str, confirm: str) -> list[str]:
    """Client-side checks, mirroring the backend rules so that obvious mistakes never reach it."""
    problems = []
    if not username:
        problems.append("Please choose a username.")
    elif not USERNAME_MIN <= len(username) <= USERNAME_MAX:
        problems.append(f"Your username must be between {USERNAME_MIN} and {USERNAME_MAX} characters long.")
    if not email:
        problems.append("Please enter your email address.")
    elif not EMAIL_RE.match(email):
        problems.append("Please enter a valid email address.")
    if not password:
        problems.append("Please choose a password.")
    elif len(password) < PASSWORD_MIN:
        problems.append(f"Your password must be at least {PASSWORD_MIN} characters long.")
    elif len(password) > PASSWORD_MAX:
        problems.append(f"Your password must be at most {PASSWORD_MAX} characters long.")
    elif not confirm:
        problems.append("Please confirm your password.")
    elif password != confirm:
        problems.append("The two passwords do not match.")
    return problems


ui.public_navbar("signup")

left, right = st.columns([1.15, 1], gap="large", vertical_alignment="center")

with left:
    html("<div class='login-title'>Start your <em>library</em> today.</div>")
    html(
        "<div class='login-copy'>Create your account to shelve the books you want to read, "
        "track what you are reading, rate what you have finished and follow other readers.</div>"
    )
    html(
        "<ul class='lp-list'><li>Four reading statuses to organise your shelves</li>"
        "<li>Ratings and reviews on every book</li>"
        "<li>Public profiles to follow other readers</li></ul>"
    )

with right:
    with st.container(key="login_card"):
        html("<h2 style='margin:0 0 .3rem'>Create your account</h2>")
        html("<div class='page-sub'>It only takes a minute.</div>")

        notice = st.session_state.pop("signup_notice", None)
        if notice:
            st.info(notice)

        with st.form("signup_form", border=False):
            username = st.text_input("Username", placeholder="choose a username", autocomplete="username")
            email = st.text_input("Email", placeholder="you@example.com", autocomplete="email")
            password = st.text_input(
                "Password", type="password", placeholder=f"at least {PASSWORD_MIN} characters",
                autocomplete="new-password",
            )
            confirm = st.text_input(
                "Confirm password", type="password", placeholder="type it again", autocomplete="new-password"
            )
            submitted = st.form_submit_button("Create account", type="primary", width="stretch")

        if submitted:
            username, email = username.strip(), email.strip()
            problems = validate(username, email, password, confirm)
            if problems:
                st.error("\n\n".join(problems))
            else:
                with st.spinner("Creating your account…"):
                    error = session.api_signup(username, email, password)
                if error:
                    st.error(error)
                else:
                    st.session_state["account_created"] = (
                        f"Your account has been created. Welcome, {username}! Log in to get started."
                    )
                    st.session_state["login_prefill"] = username
                    st.switch_page(ui.PAGES["login"])

        html(
            "<div style='text-align:center;color:var(--muted);font-size:.9rem;margin-top:.6rem'>"
            "Already have an account?</div>"
        )
        if st.button("Log in", key="signup_to_login", width="stretch"):
            st.switch_page(ui.PAGES["login"])
