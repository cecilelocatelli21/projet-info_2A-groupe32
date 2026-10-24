"""Login page: real login form (POST /login), account-created notice, optional one-click demo."""

import streamlit as st

from auth import session
from ui import components as ui
from ui.components import html
from utils.settings import demo_login_enabled

SPINES = [(h, 120 + (i * 37) % 90) for i, h in enumerate((8, 215, 340, 45, 160, 280, 20, 195, 320, 90, 250))]

ui.public_navbar("login")

# username typed on the signup page (never the password), so a new user can log in right away
if "login_prefill" in st.session_state:
    st.session_state["login_username"] = st.session_state.pop("login_prefill")

left, right = st.columns([1.15, 1], gap="large", vertical_alignment="center")

with left:
    html("<div class='login-title'>Every book you read <em>opens</em> the next.</div>")
    html(
        "<div class='login-copy'>Discover new reads, shelve them, follow your progress "
        "and share your reviews.</div>"
    )
    spines = "".join(f"<i style='--h:{h};height:{ht}px'></i>" for h, ht in SPINES)
    html(f"<div class='spines'>{spines}</div>")

with right:
    with st.container(key="login_card"):
        html("<h2 style='margin:0 0 .3rem'>Welcome back</h2>")
        html("<div class='page-sub'>Log in with your username to pick up your reading.</div>")

        public_notice = st.session_state.pop("public_notice", None)
        if public_notice:
            st.success(public_notice)
        created = st.session_state.pop("account_created", None)
        if created:
            st.success(created)
        notice = st.session_state.pop("login_notice", None)
        if notice:
            st.info(notice)

        with st.form("login_form", border=False):
            username = st.text_input(
                "Username", key="login_username", placeholder="your username", autocomplete="username"
            )
            password = st.text_input(
                "Password", type="password", placeholder="••••••••", autocomplete="current-password"
            )
            submitted = st.form_submit_button("Log in", type="primary", width="stretch")
        if submitted:
            if not username.strip() or not password:
                st.warning("Please enter your username and your password.")
            else:
                with st.spinner("Logging in…"):
                    error = session.api_login(username.strip(), password)
                if error:
                    st.error(error)
                else:
                    st.rerun()  # app.py now registers the logged-in pages and opens Home

        html(
            "<div style='text-align:center;color:var(--muted);font-size:.9rem;margin-top:.6rem'>"
            "New to Ex-Libris?</div>"
        )
        if st.button("Create account", key="login_to_signup", width="stretch"):
            st.switch_page(ui.PAGES["signup"])

        if demo_login_enabled():
            html("<div class='or-sep'><span>or</span></div>")
            if st.button("Try the demo — Camille", width="stretch", key="demo"):
                session.demo_login()
                st.rerun()
            html(
                "<div style='text-align:center;color:var(--muted);font-size:.78rem;margin-top:.5rem'>"
                "Demo mode: fictional account and data, no token, no call to the server.</div>"
            )
