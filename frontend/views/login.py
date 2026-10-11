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
        html("<h2 style='margin:0 0 .3rem'>Bon retour parmi nous</h2>")
        html("<div class='page-sub'>Connecte-toi pour retrouver ta bibliothèque.</div>")

        if demo_login_enabled():
            if st.button("Entrer dans ma bibliothèque", type="primary", width="stretch", key="demo"):
                session.demo_login()
                st.rerun()
            html(
                "<div style='text-align:center;color:var(--muted);font-size:.78rem;margin:.5rem 0 1rem'>"
                "Mode démonstration : compte fictif, aucune donnée réelle.</div>"
            )
            html("<div style='text-align:center;color:var(--muted);font-size:.8rem'>— ou avec ton compte —</div>")

        with st.form("login_form", border=False):
            username = st.text_input("Nom d'utilisateur", placeholder="ton pseudo")
            password = st.text_input("Mot de passe", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Se connecter", width="stretch")
        if submitted:
            if not username or not password:
                st.warning("Renseigne ton nom d'utilisateur et ton mot de passe.")
            else:
                error = session.api_login(username, password)
                if error:
                    st.error(error)
                else:
                    st.rerun()
