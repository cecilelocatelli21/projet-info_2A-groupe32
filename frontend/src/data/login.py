"""Login page: one-click demo access (isolated in auth.session) + real login form."""

import streamlit as st

from auth import session
from ui.components import html
from utils.settings import demo_login_enabled

SPINES = [(h, 120 + (i * 37) % 90) for i, h in enumerate((8, 215, 340, 45, 160, 280, 20, 195, 320, 90, 250))]

left, right = st.columns([1.15, 1], gap="large", vertical_alignment="center")

with left:
    html("<div class='brand' style='margin-top:2rem'><i></i>Ex-Libris <small>bibliothèque personnelle</small></div>")
    html("<div class='login-title'>Chaque livre lu <em>ouvre</em> le suivant.</div>")
    html(
        "<div class='login-copy'>Découvre de nouvelles lectures, range-les sur tes étagères, "
        "suis ta progression et partage tes critiques.</div>"
    )
    spines = "".join(f"<i style='--h:{h};height:{ht}px'></i>" for h, ht in SPINES)
    html(f"<div class='spines'>{spines}</div>")

with right:
    with st.container(key="login_card"):
        html("<div class='brand' style='font-size:1.3rem'><i></i>Ex-Libris</div>")
        html("<h2 style='margin:.9rem 0 .3rem'>Retrouvez votre bibliothèque</h2>")
        html("<div class='page-sub'>Connectez-vous avec votre pseudo pour retrouver vos lectures.</div>")

        notice = st.session_state.pop("login_notice", None)
        if notice:
            st.info(notice)

        with st.form("login_form", border=False):
            username = st.text_input("Pseudo", placeholder="votre pseudo", autocomplete="username")
            password = st.text_input("Mot de passe", type="password", placeholder="••••••••", autocomplete="current-password")
            submitted = st.form_submit_button("Se connecter", type="primary", width="stretch")
        if submitted:
            if not username.strip() or not password:
                st.warning("Renseignez votre pseudo et votre mot de passe.")
            else:
                error = session.api_login(username.strip(), password)
                if error:
                    st.error(error)
                else:
                    st.rerun()

        if demo_login_enabled():
            html("<div class='or-sep'><span>ou</span></div>")
            if st.button("Essayer la démo — Camille", width="stretch", key="demo"):
                session.demo_login()
                st.rerun()
            html(
                "<div style='text-align:center;color:var(--muted);font-size:.78rem;margin-top:.5rem'>"
                "Mode démonstration : compte fictif, données fictives, aucun jeton, aucun appel au serveur.</div>"
            )
