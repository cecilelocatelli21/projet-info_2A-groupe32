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
.hero {position:relative; min-height:420px; border-radius:18px; overflow:hidden; margin-bottom:-4.6rem;
  display:flex; align-items:flex-end; border:1px solid var(--line);}
.hero-bg {position:absolute; inset:-30px; background-size:cover; background-position:center;
  filter:blur(26px) saturate(1.3) brightness(.55); transform:scale(1.1);}
.hero-bg.gen {filter:none; transform:none; inset:0;}
.hero::after {content:""; position:absolute; inset:0;
  background:linear-gradient(90deg, rgba(12,11,16,.92) 8%, rgba(12,11,16,.35) 65%, rgba(12,11,16,.55)),
             linear-gradient(0deg, var(--bg) 0%, transparent 45%);}
.hero-in {position:relative; z-index:2; display:flex; gap:2.4rem; align-items:center; justify-content:space-between; padding:2.6rem 4rem 6.4rem 2.6rem; width:100%;}
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
.cv .cv-img {position:absolute; inset:0; background-size:cover; background-position:center; background-repeat:no-repeat;}
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
[class*="st-key-card_"]:hover {transform:scale(1.04); z-index:6;}
[class*="st-key-card_"]:hover .cv-info {opacity:1;}
[class*="st-key-card_"]:hover .cv {box-shadow:0 18px 40px rgba(0,0,0,.65), 0 0 0 1px rgba(227,176,75,.5);}
[class*="st-key-card_"] [data-testid="stElementContainer"]:has(button) {position:absolute !important; inset:0; width:100% !important; height:100% !important; z-index:4; margin:0;}
[class*="st-key-card_"] button {position:absolute !important; inset:0; width:100% !important; height:100% !important; opacity:0; cursor:pointer;}
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

/* ---- critiques cliquables et profils publics --------------------------------------- */
[class*="st-key-rev_"] {background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:1rem 1.2rem; margin-bottom:.8rem; gap:.4rem !important;}
[class*="st-key-rev_"] [class*="st-key-card_"] {max-width:130px;}
[class*="st-key-rev_"] .cv-t {font-size:.68rem; overflow-wrap:normal; word-break:normal; hyphens:auto;}
[class*="st-key-rev_"] .cv-a {font-size:.55rem;}
[data-testid="stBaseButton-tertiary"] {color:var(--gold2) !important; font-weight:600 !important; padding:0 .2rem !important; min-height:0 !important; background:transparent !important;}
[data-testid="stBaseButton-tertiary"]:hover {text-decoration:underline; color:var(--gold) !important;}
.when {color:var(--muted); font-size:.78rem;}
.rev-book {font-family:var(--serif); font-weight:700; font-size:1.05rem;}
.rev-text {margin:.2rem 0 .3rem; color:#ddd7e6; line-height:1.55;}
[class*="st-key-person_"] {padding:.2rem 0;}

/* ---- champs et onglets : indépendants de .streamlit/config.toml ---------------------- */
[data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="textarea"], [data-baseweb="select"] > div {
  background:rgba(255,255,255,.06) !important; border-color:var(--line) !important; color:var(--text) !important;}
.stTextInput input, .stTextArea textarea, [data-baseweb="select"] input {
  background:transparent !important; color:var(--text) !important; -webkit-text-fill-color:var(--text) !important;}
.stTextInput input::placeholder, .stTextArea textarea::placeholder {color:var(--muted) !important; -webkit-text-fill-color:var(--muted) !important;}
[data-testid="stWidgetLabel"] p, label p {color:var(--text) !important;}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {color:var(--muted) !important;}
[data-baseweb="tab"], [data-baseweb="tab"] p {color:var(--muted) !important;}
[data-baseweb="tab"][aria-selected="true"], [data-baseweb="tab"][aria-selected="true"] p {color:var(--gold) !important;}
[data-baseweb="tab-highlight"] {background:var(--gold) !important;}
[data-baseweb="tab-border"] {background:var(--line) !important;}
[data-testid="stBaseButton-segmented_control"], [data-testid="stBaseButton-segmented_controlActive"] {
  background:rgba(255,255,255,.06) !important; color:var(--text) !important; border:1px solid var(--line) !important;}
[data-testid="stBaseButton-segmented_controlActive"] {background:rgba(227,176,75,.2) !important; color:var(--gold2) !important; border-color:var(--gold) !important;}

/* ---- listes déroulantes (selectbox, multiselect, popover...) : texte clair sur fond sombre ------
   Streamlit y applique la couleur de texte du thème : sans ces règles on obtient du texte sombre sur
   fond sombre. Valable pour toutes les listes de l'application (statut, tri, etc.). */
[data-baseweb="select"] > div, [data-baseweb="select"] [role="combobox"], [data-baseweb="select"] input {
  color:var(--text) !important; -webkit-text-fill-color:var(--text) !important;}
[data-baseweb="select"] svg {fill:var(--muted) !important; color:var(--muted) !important;}
[data-baseweb="popover"], [data-baseweb="popover"] > div {background:transparent !important;}
[data-baseweb="popover"] [data-baseweb="menu"], [data-baseweb="popover"] [role="listbox"], [data-baseweb="popover"] ul {
  background:#1f1b29 !important; color:var(--text) !important; border:1px solid rgba(255,255,255,.16);
  border-radius:10px; box-shadow:0 18px 40px rgba(0,0,0,.6);}
[role="listbox"] li, li[role="option"], [data-baseweb="menu"] li {
  background:transparent !important; color:var(--text) !important; -webkit-text-fill-color:var(--text) !important;}
li[role="option"] *, [data-baseweb="menu"] li * {color:inherit !important; -webkit-text-fill-color:currentColor !important;}
li[role="option"]:hover, [data-baseweb="menu"] li:hover, li[role="option"][data-highlighted="true"] {
  background:rgba(227,176,75,.20) !important; color:#fff !important;}
li[role="option"][aria-selected="true"] {background:rgba(227,176,75,.30) !important; color:var(--gold2) !important; font-weight:600;}
[data-baseweb="select"] [data-baseweb="tag"] {background:rgba(227,176,75,.25) !important; color:var(--gold2) !important;}
[data-baseweb="select"] [data-baseweb="tag"] * {color:var(--gold2) !important;}
[data-testid="stPopoverBody"], [data-testid="stDialog"] [role="dialog"], [data-testid="stExpander"] details {color:var(--text);}
[data-testid="stPopoverBody"], [data-testid="stDialog"] [role="dialog"] {background:#1b1822 !important;}
[data-testid="stExpander"] details {background:rgba(255,255,255,.03) !important; border:1px solid var(--line) !important; border-radius:10px;}
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary p {color:var(--text) !important;}

/* ---- connexion --------------------------------------------------------------------- */
.login-title {font-family:var(--serif); font-size:clamp(2.4rem,4.6vw,4.2rem); line-height:1.02; margin:1.2rem 0 1rem;}
.login-title em {color:var(--gold); font-style:normal;}
.login-copy {color:#cfc8da; font-size:1.05rem; max-width:480px; line-height:1.6;}
.spines {display:flex; gap:6px; align-items:flex-end; height:210px; margin-top:2rem;}
.spines i {display:block; width:34px; border-radius:4px 4px 0 0; background:linear-gradient(180deg,hsl(var(--h) 45% 34%),hsl(var(--h) 50% 16%));
  box-shadow:inset -3px 0 0 rgba(0,0,0,.25);}
.st-key-login_card [data-testid="InputInstructions"] {display:none;}
.session-state {color:var(--muted); font-size:.78rem; margin:-.2rem 0 .4rem;}
.or-sep {display:flex; align-items:center; gap:.8rem; color:var(--muted); font-size:.8rem; margin:.4rem 0 .9rem;}
.or-sep::before,.or-sep::after {content:''; flex:1; height:1px; background:var(--line);}
.st-key-login_card {background:rgba(27,24,34,.82); border:1px solid var(--line); border-radius:18px; padding:1.6rem; backdrop-filter:blur(8px);}
[data-testid="stTextInput"] input {background:transparent !important; color:var(--text) !important; border-radius:10px !important;}
[data-baseweb="tab-list"] {gap:.4rem;}
[data-baseweb="tab"] {font-weight:500;}

/* ---- public landing page ----------------------------------------------------------- */
.st-key-lp_hero {position:relative; overflow:hidden; isolation:isolate; border-radius:20px; border:1px solid var(--line);
  min-height:580px; padding:4.5rem 3rem 3.5rem; margin-top:.4rem; justify-content:center;}
.st-key-lp_hero [data-testid="stElementContainer"] {position:relative; z-index:3;}
.st-key-lp_hero [data-testid="stElementContainer"]:has(.lp-mosaic) {position:absolute; inset:0; z-index:0; margin:0; height:auto !important;}
.st-key-lp_hero::before {content:""; position:absolute; inset:0; z-index:1; pointer-events:none;
  background:linear-gradient(90deg, rgba(12,11,16,.94) 12%, rgba(12,11,16,.62) 55%, rgba(12,11,16,.82)),
             linear-gradient(0deg, var(--bg) 0%, transparent 40%);}
.lp-mosaic {width:100%; height:100%; display:grid; grid-template-columns:repeat(8,1fr); gap:12px; align-content:center;
  transform:rotate(-7deg) scale(1.28); opacity:.6;}
.lp-mosaic .cv {box-shadow:0 6px 18px rgba(0,0,0,.5);}
.lp-kicker {color:var(--gold); text-transform:uppercase; letter-spacing:.22em; font-size:.74rem; font-weight:600;}
.lp-title {font-size:clamp(2.6rem,6vw,5.2rem) !important; line-height:1.02 !important; margin:.7rem 0 1rem !important; padding:0 !important; max-width:780px;}
.lp-title em {color:var(--gold); font-style:normal;}
.lp-sub {color:#d9d3e0; font-size:1.2rem; line-height:1.55; max-width:560px;}
.st-key-lp_actions {margin-top:1.4rem;}
.st-key-lp_actions button {min-width:170px; min-height:3rem; font-size:1.02rem;}
.lp-feats {display:grid; grid-template-columns:repeat(3,1fr); gap:1rem; margin-top:1rem;}
.lp-feat {background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:1.4rem 1.5rem;}
.lp-feat i {font-style:normal; font-size:1.7rem; display:block; margin-bottom:.4rem;}
.lp-feat b {font-family:var(--serif); font-size:1.2rem; color:var(--text);}
.lp-feat p {color:var(--muted); margin:.4rem 0 0; line-height:1.55;}
.st-key-lp_cta {margin-top:3rem; padding:2.8rem 1.5rem; text-align:center; align-items:center; border-radius:20px; border:1px solid var(--line);
  background:linear-gradient(120deg, rgba(140,47,63,.4), rgba(27,24,34,.92) 70%);}
.st-key-lp_cta h2 {margin:0 0 .3rem; font-size:2rem;}
.st-key-lp_cta_actions button {min-width:170px; min-height:3rem;}
.lp-foot {text-align:center; color:var(--muted); font-size:.8rem; padding:2rem 0 0;}
.lp-list {color:#cfc8da; line-height:1.9; margin-top:1.4rem; padding-left:1.2rem;}
.lp-list li::marker {color:var(--gold);}

/* ---- Discover / Users / fiche livre / Edit Profile --------------------------------------- */
.book-desc {color:#d9d3e0; line-height:1.65; max-width:720px; margin-top:1rem;}
.book-desc.muted {color:var(--muted); font-style:italic;}
.chip-more {background:transparent; border:1px dashed rgba(255,255,255,.25); color:var(--muted);}
.edition {padding:.55rem 0; border-bottom:1px solid var(--line);}
.edition:last-child {border-bottom:none;}
.edition b {display:block; color:var(--text);}
.edition span {color:var(--muted); font-size:.82rem;}
[class*="st-key-edit_card_"] {background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:1.2rem 1.5rem; margin:1rem 0; max-width:760px;}
[class*="st-key-edit_card_"] h3 {margin:0 0 .6rem; font-size:1.3rem;}
.st-key-edit_card_delete {border-color:rgba(220,90,100,.55); background:linear-gradient(120deg, rgba(140,47,63,.28), rgba(27,24,34,.9));}
.st-key-edit_card_delete h3 {color:#ffb1b8;}
.st-key-edit_delete_action {max-width:760px;}
.st-key-edit_delete_action button, .st-key-delete_confirm button {background:linear-gradient(135deg,#e0606f,#b3263a) !important; color:#fff !important;}
[data-testid="stTextArea"] textarea {background:transparent !important; color:var(--text) !important; -webkit-text-fill-color:var(--text) !important;}

/* neutral placeholder in grids and shelves (no cover_url, or an image that does not load): no title or
   author at rest, they appear on hover like on a real cover */
[class*="st-key-card_"] .cv-art {align-items:center; justify-content:center; padding:0;
  background:linear-gradient(160deg, hsl(var(--h) 14% 24%), hsl(var(--h) 16% 11%));}
[class*="st-key-card_"] .cv-art::before {display:none;}
[class*="st-key-card_"] .cv-art::after {content:"📖"; font-size:2.2rem; opacity:.28;}
[class*="st-key-card_"] .cv-t, [class*="st-key-card_"] .cv-a {display:none;}

/* ---- touch devices: no hover, so the title and the author stay visible on the cover ---------- */
@media (hover:none) {
  .cv-info {opacity:1; padding-top:2rem;}
  [class*="st-key-card_"]:hover {transform:none;}
}


/* ============================ refonte : cohérence, grille, recherche, critiques ============================ */
:root {--r:12px; --focus:0 0 0 3px rgba(227,176,75,.22); --ease:cubic-bezier(.2,.7,.2,1);}

/* transitions de page discrètes ; pendant une mise à jour les éléments restent presque pleins (pas de clignotement) */
@keyframes pageIn {from {opacity:0; transform:translateY(8px);} to {opacity:1; transform:none;}}
[data-testid="stMainBlockContainer"] {animation:pageIn .38s var(--ease) both;}
[data-stale="true"] {opacity:.6 !important; transition:opacity .2s !important;}
[data-testid="stDialog"] [role="dialog"] {animation:pageIn .25s var(--ease) both; border:1px solid var(--line); border-radius:16px !important;}
[data-testid="stDialog"] > div {backdrop-filter:blur(4px);}
[data-testid="stToast"] {background:#241f2e !important; color:var(--text) !important; border:1px solid var(--line); border-radius:12px !important;}
[data-testid="stAlert"] {border-radius:12px !important;}

/* indicateur de chargement discret */
[data-testid="stSpinner"] {color:var(--muted); font-size:.85rem; padding:.2rem 0;}
[data-testid="stSpinner"] p {color:var(--muted) !important;}

/* ---- boutons : une seule famille ---------------------------------------------------------- */
[data-testid^="stBaseButton"] {border-radius:10px !important; transition:background .15s, transform .15s, filter .15s, border-color .15s;}
[data-testid="stBaseButton-secondary"]:hover {border-color:rgba(255,255,255,.28) !important;}
[data-testid="stBaseButton-secondary"]:focus-visible, [data-testid="stBaseButton-primary"]:focus-visible {box-shadow:var(--focus) !important; outline:none !important;}

/* ---- champs : même fond, même bord, même focus partout ---------------------------------- */
[data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="textarea"], [data-baseweb="select"] > div {
  border-radius:10px !important; border:1px solid var(--line) !important; transition:border-color .15s, box-shadow .15s, background .15s;}
[data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within, [data-baseweb="select"]:focus-within > div {
  border-color:rgba(227,176,75,.7) !important; box-shadow:var(--focus) !important; background:rgba(255,255,255,.08) !important;}
[data-testid="stTextInput"] input {border-radius:10px !important;}

/* ---- barre de recherche (Discover, Users) : loupe discrète, pas de cadre ------------------- */
[class*="st-key-searchbar_"] {position:relative; margin:.2rem 0 1.4rem; max-width:860px;}
[class*="st-key-searchbar_"] [data-testid="stTextInput"] {width:100%;}
[class*="st-key-searchbar_"] [data-baseweb="input"], [class*="st-key-searchbar_"] [data-baseweb="base-input"] {
  background:var(--panel) !important; border-radius:999px !important; border:1px solid var(--line) !important; min-height:3.2rem;
  box-shadow:0 6px 22px rgba(0,0,0,.25);}
[class*="st-key-searchbar_"] [data-baseweb="input"]:focus-within {border-color:rgba(227,176,75,.75) !important; box-shadow:var(--focus), 0 6px 22px rgba(0,0,0,.3) !important;}
[class*="st-key-searchbar_"] input {
  font-size:1.05rem; padding:.8rem 3rem .8rem 3.1rem !important; background-color:transparent !important;
  background-repeat:no-repeat !important; background-position:1.15rem 50% !important; background-size:1.2rem !important;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23a8a1b4' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><circle cx='11' cy='11' r='7'/><path d='m20 20-3.5-3.5'/></svg>") !important;}
[class*="st-key-searchbar_"] [data-testid="InputInstructions"] {display:none;}
[class*="st-key-searchbar_"] [data-testid="stElementContainer"]:has(button) {position:absolute !important; right:.7rem; top:50%; transform:translateY(-50%); z-index:3; width:auto !important; margin:0;}
[class*="st-key-searchbar_"] button {width:2rem; height:2rem; min-height:0 !important; padding:0 !important; border-radius:50% !important;
  background:rgba(255,255,255,.1) !important; color:var(--muted) !important; font-size:.85rem;}
[class*="st-key-searchbar_"] button:hover {background:rgba(255,255,255,.2) !important; color:var(--text) !important; text-decoration:none;}
.st-key-nav [data-testid="stTextInput"] [data-baseweb="input"], .st-key-nav [data-testid="stTextInput"] [data-baseweb="base-input"] {border-radius:999px !important; background:var(--panel) !important;}

/* ---- grille de couvertures ------------------------------------------------------------------ */
[class*="st-key-grid_"] {display:grid !important; grid-template-columns:repeat(auto-fill, minmax(176px, 1fr)); gap:2rem 1.5rem !important;
  padding:.6rem .3rem 1.4rem; margin:0 -.3rem; align-items:start; width:auto !important; flex-wrap:initial !important;}
[class*="st-key-grid_"] > [data-testid="stLayoutWrapper"] {width:auto !important; min-width:0 !important; flex:none !important; max-width:none !important;}
[class*="st-key-grid_"] [class*="st-key-card_"] {width:100%;}
[class*="st-key-card_"] [data-testid="stMarkdownContainer"], [class*="st-key-card_"] [data-testid="stMarkdown"] {margin:0 !important; padding:0 !important;}
[class*="st-key-card_"] [data-testid="stElementContainer"] {margin:0;}
[class*="st-key-card_"] .cv {border-radius:10px; box-shadow:0 10px 26px rgba(0,0,0,.45); transition:box-shadow .25s var(--ease);}
[class*="st-key-card_"] {transition:transform .28s var(--ease), box-shadow .28s var(--ease);}
[class*="st-key-card_"] .cv-info {background:linear-gradient(0deg, rgba(0,0,0,.94) 12%, rgba(0,0,0,.55) 60%, transparent);
  padding-top:3.4rem; transition:opacity .28s var(--ease);}
@media (max-width:900px) {[class*="st-key-grid_"] {grid-template-columns:repeat(auto-fill, minmax(132px, 1fr)); gap:1.4rem 1rem !important;}}

/* ---- en-têtes de pages ------------------------------------------------------------------------ */
.page-title {font-size:2.4rem; margin:1.4rem 0 .15rem !important; letter-spacing:-.02em;}
.page-sub {color:var(--muted); margin-bottom:1.3rem; font-size:1rem;}
.shelf-title .count {font-family:var(--sans); font-size:.8rem; font-weight:600; color:var(--muted); background:rgba(255,255,255,.08); border-radius:999px; padding:.1rem .55rem; margin-left:.4rem; vertical-align:middle;}
.empty {background:rgba(255,255,255,.02);}

/* ---- fiche livre ---------------------------------------------------------------------------- */
.book-title {letter-spacing:-.02em;}
.book-desc {font-size:1.02rem;}
.st-key-review_form {background:var(--panel); border:1px solid var(--line); border-radius:var(--r); padding:1.1rem 1.4rem 1.2rem; margin:.4rem 0 1.4rem; max-width:860px;}
[data-testid="stFeedback"] button {font-size:1.5rem;}

/* ---- critiques : même carte pour tous, accent pour les siennes ------------------------------------ */
[class*="st-key-rev_"] {border-radius:var(--r); padding:1.15rem 1.4rem 1rem; margin-bottom:1rem; gap:.55rem !important; max-width:900px; transition:border-color .2s, background .2s;}
[class*="st-key-rev_"]:hover {border-color:rgba(255,255,255,.16);}
[class*="st-key-rev_"][class*="_mine"] {border-color:rgba(227,176,75,.38); background:linear-gradient(120deg, rgba(227,176,75,.07), var(--panel) 55%);}
.you-tag {font-size:.62rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:#1a1208; background:var(--gold); border-radius:999px; padding:.1rem .5rem;}
.rev-text {font-size:1rem; line-height:1.65; margin:.1rem 0 .2rem; white-space:pre-wrap; overflow-wrap:anywhere;}
.like-count {color:var(--muted); font-size:.85rem;}
[class*="st-key-revact_"] button[data-testid="stBaseButton-secondary"], [class*="st-key-revact_"] button[data-testid="stBaseButton-primary"] {padding:.15rem .7rem; min-height:2rem;}
[class*="st-key-revact_"] [data-testid="stBaseButton-tertiary"] {color:var(--muted) !important; font-weight:500 !important; font-size:.85rem;}
[class*="st-key-revact_"] [data-testid="stBaseButton-tertiary"]:hover {color:var(--gold2) !important;}
.stars {font-size:.95rem;}
[data-baseweb="tab-list"] {gap:1.6rem !important;}
[data-baseweb="tab"] {padding-left:.1rem !important; padding-right:.1rem !important;}
[class*="st-key-searchbar_library"] {max-width:none;}
/* utilisateurs : cartes cliquables en grille (tout le cartouche ouvre le profil) */
.st-key-people_grid {display:grid !important; grid-template-columns:repeat(auto-fill, minmax(280px, 1fr)); gap:.9rem !important; margin-top:.4rem;}
.st-key-people_grid > [data-testid="stLayoutWrapper"] {width:auto !important; min-width:0 !important;}
[class*="st-key-person_us_"] {position:relative; background:var(--panel); border:1px solid var(--line); border-radius:var(--r); padding:.9rem 1.1rem !important; gap:.9rem !important; transition:border-color .2s, transform .2s var(--ease), background .2s;}
[class*="st-key-person_us_"]:hover {border-color:rgba(227,176,75,.45); background:#211d2a; transform:translateY(-2px);}
[class*="st-key-person_us_"] [data-testid="stBaseButton-tertiary"]::after {content:""; position:absolute; inset:0; z-index:2; cursor:pointer; border-radius:var(--r);}
[class*="st-key-person_us_"] [data-testid="stBaseButton-tertiary"] {font-size:1.02rem; position:static;}
[class*="st-key-person_us_"] [data-testid="stElementContainer"] {position:static;}
.st-key-nav [data-testid="stTextInput"] input {padding-left:2.6rem !important; background-repeat:no-repeat !important; background-position:1rem 50% !important; background-size:1.05rem !important;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23a8a1b4' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><circle cx='11' cy='11' r='7'/><path d='m20 20-3.5-3.5'/></svg>") !important;}
.st-key-nav [data-testid="InputInstructions"] {display:none;}
.book-desc {margin:0; padding:1.1rem 0 .9rem; max-width:680px; font-size:1.05rem; line-height:1.7; color:#ddd7e6;}
.hero-author {margin-bottom:.5rem;}
.st-key-reading_panel {background:var(--panel); border:1px solid var(--line); border-radius:var(--r); padding:1.1rem 1.4rem 1.2rem; margin-top:1.4rem; max-width:860px; gap:.7rem !important;}
.panel-title {font-family:var(--serif); font-weight:700; font-size:1.2rem; padding-bottom:.5rem;}
.st-key-reading_panel [data-testid="stBaseButton-tertiary"] {color:var(--muted) !important; font-weight:500 !important; padding:.2rem 0 !important;}
.st-key-reading_panel [data-testid="stBaseButton-tertiary"]:hover {color:#ff9aa5 !important;}

@media (max-width:900px) {
  .st-key-lp_hero {padding:2.4rem 1.2rem 2rem; min-height:480px;}
  .lp-mosaic {grid-template-columns:repeat(4,1fr); transform:rotate(-7deg) scale(1.4);}
  .lp-feats {grid-template-columns:1fr;}
  .st-key-nav {flex-wrap:wrap;}
}

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
