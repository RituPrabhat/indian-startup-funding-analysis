import json
from urllib.parse import quote

import joblib
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Startup Deal-Size Predictor", layout="wide",
                   initial_sidebar_state="collapsed")

REPO = "https://github.com/RituPrabhat/indian-startup-funding-analysis"
AUTHOR = "Ritu Prabhat"


# ---------- generated background images (SVG, no files needed) ----------
def hero_svg():
    p = ["<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 420' preserveAspectRatio='xMidYMid slice'>",
         "<defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'>"
         "<stop offset='0' stop-color='#0a1f3d'/><stop offset='1' stop-color='#0f4c5c'/></linearGradient></defs>",
         "<rect width='1200' height='420' fill='url(#g)'/>"]
    for x in range(0, 1201, 80):
        p.append(f"<line x1='{x}' y1='0' x2='{x}' y2='420' stroke='white' stroke-opacity='0.05'/>")
    for y in range(0, 421, 70):
        p.append(f"<line x1='0' y1='{y}' x2='1200' y2='{y}' stroke='white' stroke-opacity='0.05'/>")
    heights = [60, 85, 110, 100, 150, 195, 250, 310, 270]
    pts = []
    for i, h in enumerate(heights):
        x = 560 + i * 66
        p.append(f"<rect x='{x}' y='{420 - h}' width='44' height='{h}' fill='white' fill-opacity='0.08'/>")
        pts.append(f"{x + 22},{420 - h - 18}")
    p.append(f"<polyline points='{' '.join(pts)}' fill='none' stroke='#f2b84b' stroke-width='3' stroke-opacity='0.85'/>")
    for pt in pts:
        cx, cy = pt.split(",")
        p.append(f"<circle cx='{cx}' cy='{cy}' r='5' fill='#f2b84b'/>")
    p.append("</svg>")
    return "".join(p)


PAGE_SVG = ("<svg xmlns='http://www.w3.org/2000/svg' width='48' height='48'>"
            "<path d='M48 0H0V48' fill='none' stroke='#14213d' stroke-opacity='0.05'/></svg>")

HERO_URI = "data:image/svg+xml," + quote(hero_svg(), safe="")
PAGE_URI = "data:image/svg+xml," + quote(PAGE_SVG, safe="")

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@600;700&family=Inter:wght@400;500;600&display=swap');
#MainMenu, footer, header {visibility: hidden;}
section[data-testid="stSidebar"], div[data-testid="stSidebarCollapsedControl"],
div[data-testid="collapsedControl"] {display: none;}
.stApp {background-color: #f7f5f0; background-image: url("__PAGE__"); color: #14213d;
        font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif;}
.block-container {max-width: 1080px; padding-top: 1rem; padding-bottom: 3rem;}

/* ---------- top bar ---------- */
.brand {display: flex; align-items: center; gap: 10px; padding: 8px 0;}
.brand span {font-family: 'Fraunces', Georgia, serif; font-weight: 700; font-size: 1.2rem; color: #14213d;}
div[data-testid="stRadio"] div[role="radiogroup"] {justify-content: flex-end; gap: 4px;}
div[data-testid="stRadio"] label {padding: 8px 16px; border-bottom: 2px solid transparent;
    border-radius: 0; cursor: pointer; font-weight: 500;}
div[data-testid="stRadio"] label > div:first-child {display: none;}
div[data-testid="stRadio"] label:has(input:checked) {border-bottom: 2px solid #0f766e;
    color: #0f766e; font-weight: 600;}
.topline {border-bottom: 1px solid #e3ded3; margin: 2px 0 20px 0;}

/* ---------- hero ---------- */
.hero {border-radius: 10px; padding: 46px 44px; color: #ffffff; margin-bottom: 26px;
       background: linear-gradient(90deg, rgba(10,31,61,.94) 0%, rgba(10,31,61,.6) 62%, rgba(10,31,61,.15) 100%),
                   url("__HERO__");
       background-size: cover; background-position: center;}
.hero h1 {font-family: 'Fraunces', Georgia, serif; font-size: 2.5rem; line-height: 1.15; margin: 0 0 12px 0;
          padding: 0; color: #ffffff; font-weight: 700; max-width: 620px;}
.hero p {color: #cfd8e3; font-size: 1.02rem; line-height: 1.6; margin: 0 0 22px 0; max-width: 560px;}
.stats {display: flex; flex-wrap: wrap; gap: 30px;}
.stats div {border-left: 2px solid #f2b84b; padding-left: 12px;}
.stats b {display: block; font-family: 'Fraunces', Georgia, serif; font-size: 1.4rem; color: #ffffff;}
.stats span {font-size: .8rem; color: #b8c4d3; letter-spacing: .3px;}
.hero.small {padding: 34px 44px;}
.hero.small h1 {font-size: 2rem; margin-bottom: 6px;}
.hero.small p {margin: 0;}

/* ---------- inputs and result ---------- */
.section-title {font-family: 'Fraunces', Georgia, serif; font-size: 1.25rem; font-weight: 700;
                color: #14213d; margin: 0 0 10px 0;}
div[data-testid="stVerticalBlockBorderWrapper"] {background: #ffffff; border-radius: 10px;}
.result {background: #ffffff; border: 1px solid #e3ded3; border-top: 4px solid var(--c);
         border-radius: 10px; padding: 26px 28px;}
.result .kicker {font-size: .78rem; letter-spacing: 1.2px; text-transform: uppercase; color: #6b7280;}
.result .band {font-family: 'Fraunces', Georgia, serif; font-size: 2.8rem; font-weight: 700;
               color: var(--c); line-height: 1.1; margin: 4px 0 2px 0;}
.result .range {font-size: 1.05rem; font-weight: 600; color: #14213d; margin-bottom: 4px;}
.result .sel {font-size: .85rem; color: #6b7280; margin-bottom: 10px;}
.result .desc {color: #4b5563; font-size: .95rem; line-height: 1.55;}
.barrow {display: flex; align-items: center; margin: 12px 0;}
.barlabel {width: 70px; font-size: .9rem; color: #374151;}
.track {flex: 1; height: 8px; background: #ece8df; border-radius: 4px; overflow: hidden;}
.fill {height: 100%;}
.pct {width: 52px; text-align: right; font-weight: 600; font-size: .9rem; color: #14213d;}
.note {margin-top: 14px; padding: 10px 14px; background: #fdf6e3; border: 1px solid #ecd9a0;
       color: #7a5b0f; border-radius: 6px; font-size: .88rem;}

/* ---------- how it works ---------- */
.step {border-top: 2px solid #14213d; padding-top: 12px; margin-bottom: 12px;}
.step .n {font-family: 'Fraunces', Georgia, serif; font-size: 1.5rem; color: #0f766e; font-weight: 700;}
.step .t {font-weight: 600; color: #14213d; margin: 2px 0 4px 0;}
.step .d {color: #4b5563; font-size: .92rem; line-height: 1.55;}

/* ---------- help page ---------- */
.info {background: #ffffff; border: 1px solid #e3ded3; border-left: 4px solid #0f766e;
       border-radius: 6px; padding: 18px 22px; margin-top: 12px;}
.info h4 {font-family: 'Fraunces', Georgia, serif; margin: 0 0 6px 0; color: #14213d; font-size: 1.2rem;}
.info p {margin: 0 0 8px 0; color: #4b5563; line-height: 1.6; font-size: .95rem;}
.tag {display: inline-block; background: #e6f2f0; color: #0f5f58; border-radius: 4px;
      padding: 3px 10px; font-size: .8rem; font-weight: 600; margin: 2px 6px 2px 0;}
.bandcard {background: #ffffff; border: 1px solid #e3ded3; border-top: 4px solid var(--c);
           border-radius: 8px; padding: 16px 18px; margin-bottom: 10px;}
.bandcard .b {font-family: 'Fraunces', Georgia, serif; font-weight: 700; font-size: 1.4rem; color: var(--c);}
.bandcard .r {font-weight: 600; color: #14213d; margin: 2px 0 6px 0;}
.bandcard .x {color: #4b5563; font-size: .9rem; line-height: 1.5;}
.footer {text-align: center; color: #6b7280; font-size: .85rem; margin-top: 34px; padding-top: 16px;
         border-top: 1px solid #e3ded3;}
.footer a {color: #0f766e; text-decoration: none; font-weight: 600;}

/* ---------- phones ---------- */
@media (max-width: 768px) {
  .block-container {padding-left: 1rem; padding-right: 1rem;}
  .hero {padding: 28px 20px;}
  .hero h1 {font-size: 1.75rem;}
  .hero.small {padding: 24px 20px;}
  .hero.small h1 {font-size: 1.5rem;}
  .stats {gap: 18px;}
  .result {padding: 20px 18px;}
  .result .band {font-size: 2.2rem;}
  div[data-testid="stRadio"] div[role="radiogroup"] {justify-content: flex-start;}
}
"""
st.markdown("<style>" + CSS.replace("__HERO__", HERO_URI).replace("__PAGE__", PAGE_URI) + "</style>",
            unsafe_allow_html=True)


@st.cache_resource
def load_assets():
    model = joblib.load("deal_size_model.joblib")
    with open("app_options.json") as f:
        opts = json.load(f)
    return model, opts


model, opts = load_assets()

BANDS = ["Small", "Medium", "Large"]
COLORS = {"Small": "#2f6f9f", "Medium": "#d08a1e", "Large": "#b4443c"}
RANGE = {"Small": "Under $1 million", "Medium": "$1 million to $10 million", "Large": "Over $10 million"}
DESC = {
    "Small": "Deals with this profile are usually small, typical of very early rounds.",
    "Medium": "Deals with this profile usually fall in the middle range of funding rounds.",
    "Large": "Deals with this profile are usually large, typical of later and bigger rounds.",
}

STAGE_ORDER = ["Pre-Seed", "Seed/Angel", "Pre-Series A/B", "Series A", "Series B",
               "Series C", "Series D+", "Private Equity", "Unknown/Other"]
stages = [s for s in STAGE_ORDER if s in opts["stages"]]
stages += [s for s in opts["stages"] if s not in stages]

STAGE_INFO = {
    "Pre-Seed": ("The earliest money, often when there is only an idea or a prototype. It usually comes from "
                 "founders' networks, incubators or very small funds.", "Tends to be small"),
    "Seed/Angel": ("The first outside money for an early product. It mostly comes from angel investors and "
                   "seed funds, and is used to build the first version and find the first customers.",
                   "Tends to be small"),
    "Pre-Series A/B": ("Rounds labelled between the main stages, such as pre-Series A. They bridge the gap "
                       "between two larger rounds.", "Tends to be small to medium"),
    "Series A": ("The product works and customers are arriving. Venture capital firms invest so the company "
                 "can build its team and grow.", "Tends to be medium"),
    "Series B": ("The business is growing steadily. The money is used to expand to new cities or products "
                 "and to scale operations.", "Tends to be medium to large"),
    "Series C": ("An established company expanding widely, entering new markets or buying other companies.",
                 "Tends to be large"),
    "Series D+": ("Series D and every later round. These are mature, high-value companies, often close to a "
                  "stock-market listing. They are the biggest rounds in the data.", "Tends to be large"),
    "Private Equity": ("Large investment funds buying a stake in an established company.", "Tends to be large"),
    "Unknown/Other": ("Deals where the source did not state a stage, or the label did not fit any group. "
                      "The model treats these as their own group.", "Varies"),
}

SECTOR_INFO = {
    "AgriTech": "Technology for farming and the food supply chain, such as farm marketplaces and crop tools.",
    "Consumer Internet": "Consumer-facing apps and websites, such as social, content, services and marketplaces.",
    "E-commerce & Retail": "Online shopping and retail businesses, including marketplaces and direct-to-consumer brands.",
    "Tech & SaaS": "Software products sold to businesses, plus general technology companies.",
    "FinTech": "Financial technology: payments, lending, insurance technology and investing apps.",
    "EdTech": "Education technology: online learning, coaching and skills platforms.",
    "HealthTech": "Healthcare technology: health apps, diagnostics, online doctors and pharmacies.",
    "Real Estate": "Property technology: listings, rentals, co-working and construction tech.",
    "Logistics": "Delivery, transport and supply-chain companies.",
}

# ---------- top navigation ----------
nav_l, nav_r = st.columns([3, 2])
with nav_l:
    st.markdown(
        '<div class="brand"><svg width="28" height="28" viewBox="0 0 28 28">'
        '<rect x="3" y="15" width="5" height="10" fill="#0f766e"/>'
        '<rect x="11" y="9" width="5" height="16" fill="#0f766e"/>'
        '<rect x="19" y="3" width="5" height="22" fill="#d08a1e"/></svg>'
        "<span>Deal-Size Predictor</span></div>",
        unsafe_allow_html=True,
    )
with nav_r:
    page = st.radio("Navigate", ["Predict", "Help & Guide"], horizontal=True, label_visibility="collapsed")
st.markdown('<div class="topline"></div>', unsafe_allow_html=True)


def footer():
    st.markdown(
        f'<div class="footer">Built by <b>{AUTHOR}</b> &nbsp;·&nbsp; '
        f'<a href="{REPO}" target="_blank">View code on GitHub</a><br>'
        "Educational project. Estimates come from historical data and are not financial advice.</div>",
        unsafe_allow_html=True,
    )


# =====================================================================
# PAGE 1: PREDICT
# =====================================================================
if page == "Predict":
    st.markdown(
        '<div class="hero"><h1>Estimate the size of an Indian startup funding round</h1>'
        "<p>Describe a deal and see whether rounds like it are usually small, medium or large, "
        "based on real funding data.</p>"
        '<div class="stats"><div><b>4,300+</b><span>deals analysed</span></div>'
        "<div><b>2015 to 2022</b><span>period covered</span></div>"
        "<div><b>18</b><span>sectors</span></div></div></div>",
        unsafe_allow_html=True,
    )

    left, right = st.columns([5, 6], gap="large")

    with left:
        with st.container(border=True):
            st.markdown('<div class="section-title">Describe the deal</div>', unsafe_allow_html=True)
            stage = st.selectbox("Funding stage", stages)
            sector = st.selectbox("Sector", opts["sectors"])
            city = st.selectbox("City", opts["cities"])
            year = st.slider("Year", opts["year_min"], opts["year_max"], opts["year_max"])
        st.caption("Not sure what an option means? Open Help & Guide from the menu above.")

    row = pd.DataFrame([{"Sector": sector, "City_Group": city, "Stage_Std": stage, "Year": year}])
    proba = pd.Series(model.predict_proba(row)[0], index=model.classes_)[BANDS]
    best = proba.idxmax()

    bars = "".join(
        f'<div class="barrow"><div class="barlabel">{b}</div>'
        f'<div class="track"><div class="fill" style="width:{proba[b] * 100:.1f}%;background:{COLORS[b]}"></div></div>'
        f'<div class="pct">{proba[b]:.0%}</div></div>'
        for b in BANDS
    )
    note = ""
    if proba.max() < 0.5:
        note = ('<div class="note">The probabilities are close together, so the model is not very sure '
                "about this one. Treat it as a rough estimate.</div>")

    with right:
        st.markdown(
            f'<div class="result" style="--c:{COLORS[best]}">'
            '<div class="kicker">Predicted deal size</div>'
            f'<div class="band">{best}</div>'
            f'<div class="range">{RANGE[best]}</div>'
            f'<div class="sel">{stage} &nbsp;·&nbsp; {sector} &nbsp;·&nbsp; {city} &nbsp;·&nbsp; {year}</div>'
            f'<div class="desc">{DESC[best]}</div>'
            f'<div style="margin-top:16px">{bars}</div>'
            f"{note}</div>",
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-title" style="margin-top:30px">How it works</div>', unsafe_allow_html=True)
    s1, s2, s3 = st.columns(3, gap="large")
    steps = [
        ("01", "Choose the details", "Pick the funding stage, sector, city and year of a deal."),
        ("02", "The model compares", "It looks for similar deals among thousands of real past rounds."),
        ("03", "Read the size band", "You see whether such deals are usually small, medium or large."),
    ]
    for col, (n, t, d) in zip((s1, s2, s3), steps):
        col.markdown(f'<div class="step"><div class="n">{n}</div><div class="t">{t}</div>'
                     f'<div class="d">{d}</div></div>', unsafe_allow_html=True)
    footer()

# =====================================================================
# PAGE 2: HELP & GUIDE
# =====================================================================
else:
    st.markdown('<div class="hero small"><h1>Help and guide</h1>'
                "<p>Click a tab to see what each option means and how to read the result.</p></div>",
                unsafe_allow_html=True)

    tabs = st.tabs(["Funding stage", "Sector", "City", "Year", "Size bands", "Reading the result"])

    with tabs[0]:
        st.write("A startup raises money in rounds. Pick a stage to see what it means.")
        pick = st.selectbox("Choose a stage", stages, key="help_stage")
        text, tend = STAGE_INFO.get(pick, ("A funding stage used in the dataset.", "Varies"))
        st.markdown(f'<div class="info"><h4>{pick}</h4><p>{text}</p><span class="tag">{tend}</span></div>',
                    unsafe_allow_html=True)
        st.caption("Stage is the strongest clue the model uses, because later rounds are usually larger.")

    with tabs[1]:
        st.write("The sector is the industry the startup works in. Pick one to see what it covers.")
        pick = st.selectbox("Choose a sector", opts["sectors"], key="help_sector")
        text = SECTOR_INFO.get(pick, f"Startups grouped under '{pick}' in the dataset. Original industry "
                                     "descriptions were grouped into 18 sectors using keywords.")
        st.markdown(f'<div class="info"><h4>{pick}</h4><p>{text}</p></div>', unsafe_allow_html=True)

    with tabs[2]:
        chips = "".join(f'<span class="tag">{c}</span>' for c in opts["cities"])
        st.markdown(
            '<div class="info"><h4>City</h4>'
            "<p>The city where the startup is based. Cities with many deals are kept as they are. "
            'All smaller cities are combined into one group called "Other".</p>'
            f"{chips}</div>",
            unsafe_allow_html=True,
        )

    with tabs[3]:
        st.markdown(
            '<div class="info"><h4>Year</h4>'
            f"<p>The year the round was announced. The data covers {opts['year_min']} to {opts['year_max']} "
            "(2022 only up to May), so the slider stops there. Funding sizes changed over time, "
            "which is why the year matters a little.</p></div>",
            unsafe_allow_html=True,
        )

    with tabs[4]:
        info = {
            "Small": "Typical of the very first rounds, where a startup is just getting started.",
            "Medium": "Typical of growing startups that have a working product and customers.",
            "Large": "Typical of established companies raising big rounds to scale up.",
        }
        cols = st.columns(3, gap="medium")
        for col, b in zip(cols, BANDS):
            col.markdown(
                f'<div class="bandcard" style="--c:{COLORS[b]}"><div class="b">{b}</div>'
                f'<div class="r">{RANGE[b]}</div><div class="x">{info[b]}</div></div>',
                unsafe_allow_html=True,
            )

    with tabs[5]:
        st.markdown(
            '<div class="info"><h4>How to read the result</h4>'
            "<p><b>The large word</b> (Small, Medium or Large) is the size band the model thinks is most likely.</p>"
            "<p><b>The three bars</b> show how likely each band is. They add up to 100%.</p>"
            "<p><b>If one bar is much longer</b> than the others, the model is fairly sure. "
            "If the bars are close, the model is unsure and the answer is only a rough guide.</p>"
            "<p><b>What it cannot do:</b> it does not know a company's name, product, revenue or team, "
            "so it cannot say how much one specific startup will raise. It estimates the typical size "
            "of a round with this profile.</p></div>",
            unsafe_allow_html=True,
        )
    footer()
