"""Ex-Libris visual identity: deep ink background, antique-gold accent, serif headlines.

Everything visual lives here (one stylesheet) so pages stay free of styling details.
"""

from __future__ import annotations

import streamlit as st

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Inter:wght@400;500;600&display=swap');

:root {
  --bg:#0c0b10; --bg2:#14121a; --panel:#1b1822; --line:rgba(255,255,255,.09);
  --text:#f4efe6; --muted:#a8a1b4; --gold:#e3b04b; --gold2:#f3cf86; --wine:#8c2f3f;
  --gut:2.4rem; --serif:'Fraunces', Georgia, serif; --sans:'Inter', system-ui, sans-serif;
}

/* ---- chrome Streamlit -------------------------------------------------------------- */
header[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], footer, #MainMenu {display:none !important;}
.stApp {
  background:
    radial-gradient(1200px 600px at 85% -10%, rgba(140,47,63,.28), transparent 60%),
    radial-gradient(900px 500px at -10% 10%, rgba(227,176,75,.10), transparent 55%),
    var(--bg);
  color:var(--text); font-family:var(--sans);
}
.block-container {padding:0 var(--gut) 4rem !important; max-width:1680px !important;}
h1,h2,h3 {font-family:var(--serif) !important; letter-spacing:-.01em; color:var(--text);}
p, label, span, li {font-family:var(--sans);}
a {color:var(--gold2);}
hr {border-color:var(--line) !important;}

/* ---- barre de navigation ----------------------------------------------------------- */
[data-testid="stLayoutWrapper"]:has(> .st-key-nav) {position:sticky; top:0; z-index:100; margin:0 calc(-1 * var(--gut)) 1rem; width:calc(100% + 2 * var(--gut)) !important; max-width:none !important;}
.st-key-nav {
  padding:.7rem var(--gut);
  background:linear-gradient(180deg, rgba(12,11,16,.96), rgba(12,11,16,.72));
  backdrop-filter:blur(14px); border-bottom:1px solid var(--line); align-items:center;
}
.brand {font-family:var(--serif); font-weight:700; font-size:1.55rem; color:var(--gold); line-height:1;
  display:flex; align-items:center; gap:.5rem; white-space:nowrap;}
.brand i {display:inline-block; width:.8rem; height:1.35rem; background:linear-gradient(var(--gold),var(--wine));
  clip-path:polygon(0 0,100% 0,100% 100%,50% 78%,0 100%);}
.brand small {font-family:var(--sans); font-weight:500; font-size:.62rem; letter-spacing:.22em; color:var(--muted); text-transform:uppercase;}
[data-testid="stPageLink-NavLink"] {border-radius:8px; padding:.35rem .8rem !important; background:transparent !important;}
[data-testid="stPageLink-NavLink"] p {color:var(--muted); font-weight:500; font-size:.95rem;}
[data-testid="stPageLink-NavLink"]:hover p {color:var(--text);}
[data-testid="stPageLink-NavLink"][aria-current="page"] p {color:var(--gold); font-weight:600;}
.st-key-nav [data-testid="stTextInput"] input {
  background:rgba(255,255,255,.06) !important; border:1px solid var(--line) !important;
  border-radius:999px !important; color:var(--text) !important; padding:.5rem 1rem !important;}
.st-key-nav [data-testid="stTextInput"] > div > div {background:transparent !important; border:none !important;}
.st-key-nav [data-testid="stPopoverButton"] {
  width:2.3rem; height:2.3rem; border-radius:50% !important; padding:0 !important; min-height:0 !important;
  background:linear-gradient(135deg,var(--gold),var(--wine)) !important; color:#1a1208 !important; font-weight:700; border:none !important; justify-content:center;}
.st-key-nav [data-testid="stPopoverButton"] svg {display:none;}

/* ---- boutons ----------------------------------------------------------------------- */
[data-testid="stBaseButton-primary"], [data-testid="stBaseButton-primaryFormSubmit"] {
  background:linear-gradient(135deg,var(--gold2),var(--gold)) !important; color:#1a1208 !important;
  border:none !important; border-radius:8px !important; font-weight:600 !important; transition:transform .15s, filter .15s;}
[data-testid="stBaseButton-primary"]:hover {filter:brightness(1.08); transform:translateY(-1px);}
[data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-secondaryFormSubmit"] {
  background:rgba(255,255,255,.08) !important; color:var(--text) !important; border:1px solid var(--line) !important;
  border-radius:8px !important; font-weight:500 !important;}
[data-testid="stBaseButton-secondary"]:hover {background:rgba(255,255,255,.15) !important;}

/* ---- bannière ---------------------------------------------------------------------- */
.hero {position:relative; min-height:460px; border-radius:18px; overflow:hidden; margin-bottom:-4.6rem;
  display:flex; align-items:flex-end; border:1px solid var(--line);}
.hero-bg {position:absolute; inset:-30px; background-size:cover; background-position:center;
  filter:blur(26px) saturate(1.3) brightness(.55); transform:scale(1.1);}
.hero-bg.gen {filter:none; transform:none; inset:0;}
.hero::after {content:""; position:absolute; inset:0;
  background:linear-gradient(90deg, rgba(12,11,16,.92) 8%, rgba(12,11,16,.35) 65%, rgba(12,11,16,.55)),
             linear-gradient(0deg, var(--bg) 0%, transparent 45%);}
.hero-in {position:relative; z-index:2; display:flex; gap:2.4rem; align-items:flex-end; padding:2.4rem 2.6rem 6.6rem; width:100%;}
.hero-copy {flex:1; max-width:640px;}
.hero-kicker {color:var(--gold); text-transform:uppercase; letter-spacing:.2em; font-size:.72rem; font-weight:600;}
.hero h1 {font-size:clamp(2.2rem,4.4vw,4rem); line-height:1.02; margin:.5rem 0 .3rem; padding:0;}
.hero-author {color:var(--gold2); font-size:1.1rem; margin-bottom:.7rem;}
.hero-desc {color:#d9d3e0; font-size:1rem; line-height:1.55; max-width:560px; display:-webkit-box;
  -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden;}
.hero-cover {width:210px; flex:none; box-shadow:0 30px 60px rgba(0,0,0,.6); border-radius:8px; transform:rotate(2deg);}
.st-key-hero_actions {position:relative; z-index:5; padding:0 2.6rem; max-width:560px; margin-bottom:2.4rem;}

/* ---- couvertures et cartes --------------------------------------------------------- */
.cv {position:relative; aspect-ratio:2/3; border-radius:8px; overflow:hidden; background:#222;
  box-shadow:0 8px 24px rgba(0,0,0,.45);}
.cv-art {position:absolute; inset:0; padding:17% 11% 12%; display:flex; flex-direction:column; justify-content:space-between;
  background:
    linear-gradient(160deg, hsl(var(--h) 45% 30%), hsl(calc(var(--h) + 40) 50% 14%));
  border-left:6px solid rgba(0,0,0,.28);}
.cv-art::before {content:""; position:absolute; left:11%; right:11%; top:42%; height:1px; background:rgba(255,255,255,.35);}
.cv-t {font-family:var(--serif); font-weight:700; font-size:1.05rem; line-height:1.15; color:#fff; text-shadow:0 1px 6px rgba(0,0,0,.4);}
.cv-a {font-size:.68rem; letter-spacing:.08em; text-transform:uppercase; color:rgba(255,255,255,.75);}
.cv img {position:absolute; inset:0; width:100%; height:100%; object-fit:cover; display:block;}
.cv-info {position:absolute; inset:auto 0 0 0; padding:2.6rem .7rem .7rem; opacity:0; transition:opacity .25s;
  background:linear-gradient(0deg, rgba(0,0,0,.92), transparent); font-size:.76rem; color:#fff;}
.cv-info b {display:block; font-size:.88rem; line-height:1.2; margin-bottom:.15rem;}
.cv-info span {color:var(--gold2);}
.chip {display:inline-block; padding:.12rem .5rem; border-radius:999px; font-size:.68rem; font-weight:600;
  background:rgba(255,255,255,.12); color:var(--text); margin:.15rem .25rem .15rem 0; white-space:nowrap;}
.chip.s-to-read {background:rgba(120,160,255,.22); color:#b9ccff;}
.chip.s-in-progress {background:rgba(227,176,75,.25); color:var(--gold2);}
.chip.s-read {background:rgba(90,200,140,.22); color:#a6ecc6;}
.chip.s-abandoned {background:rgba(220,90,100,.22); color:#ffb1b8;}
.cv .chip {position:absolute; top:.5rem; left:.5rem; margin:0; backdrop-filter:blur(6px); z-index:2;}

[class*="st-key-card_"] {position:relative; gap:0 !important; border-radius:8px; transition:transform .25s ease, box-shadow .25s ease;}
[class*="st-key-card_"]:hover {transform:scale(1.05); z-index:6;}
[class*="st-key-card_"]:hover .cv-info {opacity:1;}
[class*="st-key-card_"]:hover .cv {box-shadow:0 18px 40px rgba(0,0,0,.65), 0 0 0 1px rgba(227,176,75,.5);}
[class*="st-key-card_"] [data-testid="stElementContainer"]:has(button) {position:absolute !important; inset:0; z-index:4; margin:0;}
[class*="st-key-card_"] button {width:100% !important; height:100% !important; opacity:0; cursor:pointer;}
.card-meta {padding:.5rem .15rem .9rem; font-size:.8rem; line-height:1.25;}
.card-meta b {display:block; color:var(--text); font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;}
.card-meta span {color:var(--muted); font-size:.74rem;}

/* ---- rangées horizontales ---------------------------------------------------------- */
[class*="st-key-row_"] {overflow-x:auto !important; overflow-y:visible !important; flex-wrap:nowrap !important;
  gap:1rem !important; padding:.9rem .4rem 1.6rem; margin:0 -.4rem; scrollbar-width:thin; scrollbar-color:#3b3647 transparent;}
[class*="st-key-row_"] > [data-testid="stLayoutWrapper"] {flex:0 0 176px; width:176px; min-width:176px;}
.shelf-title {font-family:var(--serif); font-size:1.5rem; font-weight:700; margin:1.6rem 0 0; color:var(--text);}
.shelf-sub {color:var(--muted); font-size:.85rem; margin-top:.1rem;}

/* ---- divers ------------------------------------------------------------------------ */
.banner {border:1px solid rgba(227,176,75,.4); background:rgba(227,176,75,.08); color:var(--gold2);
  border-radius:10px; padding:.6rem 1rem; font-size:.85rem; margin:.4rem 0 1rem;}
.demo-pill {display:inline-block; font-size:.62rem; letter-spacing:.12em; text-transform:uppercase; font-weight:600;
  border:1px solid rgba(227,176,75,.5); color:var(--gold2); border-radius:999px; padding:.15rem .6rem;}
.page-title {font-size:2.3rem; margin:1.2rem 0 .2rem;}
.page-sub {color:var(--muted); margin-bottom:1rem;}
.stars {color:var(--gold); letter-spacing:.08em; font-size:1rem;}
.stars .off {color:#4a4553;}
.empty {text-align:center; padding:3rem 1rem; border:1px dashed var(--line); border-radius:14px; color:var(--muted);}
.empty b {display:block; font-family:var(--serif); font-size:1.3rem; color:var(--text); margin-bottom:.3rem;}
.panel {background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:1.1rem 1.3rem; margin-bottom:.8rem;}
.panel .who {font-weight:600;} .panel .when {color:var(--muted); font-size:.78rem; margin-left:.4rem;}
.panel p {margin:.4rem 0 0; color:#ddd7e6; line-height:1.55;}
.stat {background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:1rem 1.2rem;}
.stat b {display:block; font-family:var(--serif); font-size:2rem; color:var(--gold); line-height:1;}
.stat span {color:var(--muted); font-size:.8rem;}
.avatar {width:96px; height:96px; border-radius:50%; flex:none; display:flex; align-items:center; justify-content:center;
  font-family:var(--serif); font-size:2.8rem; font-weight:700; color:#1a1208;
  background:linear-gradient(135deg,var(--gold2),var(--gold) 45%,var(--wine)); box-shadow:0 10px 30px rgba(0,0,0,.5);}
.avatar.sm {width:40px; height:40px; font-size:1.1rem;}
.profile-head {display:flex; gap:1.6rem; align-items:center; padding:2rem; border-radius:18px; border:1px solid var(--line);
  background:linear-gradient(120deg, rgba(140,47,63,.35), rgba(27,24,34,.9) 60%); margin-top:.6rem;}
.profile-head h1 {margin:0; font-size:2.2rem;} .profile-head p {margin:.3rem 0 0; color:#d9d3e0; max-width:620px;}
.person {display:flex; gap:.8rem; align-items:center; padding:.6rem .2rem;}
.person b {display:block;} .person span {color:var(--muted); font-size:.8rem;}
.bar {height:8px; border-radius:6px; background:rgba(255,255,255,.08); overflow:hidden; margin:.2rem 0 .8rem;}
.bar i {display:block; height:100%; background:linear-gradient(90deg,var(--wine),var(--gold));}
.bar-l {display:flex; justify-content:space-between; font-size:.82rem; color:var(--muted);}
.book-title {font-size:clamp(2rem,3.6vw,3.2rem); line-height:1.05; margin:0 0 .3rem;}
.meta-grid {display:grid; grid-template-columns:repeat(auto-fit,minmax(130px,1fr)); gap:.6rem; margin:1rem 0;}
.meta-grid div {background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:.6rem .8rem;}
.meta-grid span {display:block; color:var(--muted); font-size:.7rem; text-transform:uppercase; letter-spacing:.08em;}
.meta-grid b {font-weight:600; font-size:.95rem;}

/* ---- connexion --------------------------------------------------------------------- */
.login-title {font-family:var(--serif); font-size:clamp(2.4rem,4.6vw,4.2rem); line-height:1.02; margin:1.2rem 0 1rem;}
.login-title em {color:var(--gold); font-style:normal;}
.login-copy {color:#cfc8da; font-size:1.05rem; max-width:480px; line-height:1.6;}
.spines {display:flex; gap:6px; align-items:flex-end; height:210px; margin-top:2rem;}
.spines i {display:block; width:34px; border-radius:4px 4px 0 0; background:linear-gradient(180deg,hsl(var(--h) 45% 34%),hsl(var(--h) 50% 16%));
  box-shadow:inset -3px 0 0 rgba(0,0,0,.25);}
.st-key-login_card {background:rgba(27,24,34,.82); border:1px solid var(--line); border-radius:18px; padding:1.6rem; backdrop-filter:blur(8px);}
[data-testid="stTextInput"] input {background:rgba(255,255,255,.05) !important; color:var(--text) !important; border-radius:8px !important;}
[data-baseweb="tab-list"] {gap:.4rem;}
[data-baseweb="tab"] {font-weight:500;}

@media (max-width:900px) {
  .block-container {padding:0 var(--gut) 3rem !important;}
  :root {--gut:1rem;}
  .hero {margin-bottom:0;} .hero-cover {display:none;} .hero-in {padding:1.4rem 1.2rem 1.6rem;}
  .st-key-hero_actions {padding:0; margin-top:.8rem;}
  [class*="st-key-row_"] > [data-testid="stLayoutWrapper"] {flex-basis:140px; width:140px; min-width:140px;}
  .profile-head {flex-direction:column; text-align:center;}
}
"""


def inject_css() -> None:
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
