import json
import joblib
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Startup Deal-Size Predictor", page_icon="📊",
                   layout="wide", initial_sidebar_state="expanded")

REPO = "https://github.com/RituPrabhat/indian-startup-funding-analysis"
AUTHOR = "Ritu Prabhat"

CSS = """
#MainMenu, footer {visibility: hidden;}
.stApp {background: #f5f7fb; color: #0f172a;}
.block-container {max-width: 1100px; padding-top: 1.2rem; padding-bottom: 3rem;}

/* ---------- sidebar ---------- */
section[data-testid="stSidebar"] {background: #ffffff; border-right: 1px solid #e5e7eb;}
.brand {padding: 6px 4px 14px 4px; border-bottom: 1px solid #eef0f4; margin-bottom: 14px;}
.brand .logo {font-size: 1.6rem;}
.brand .name {font-weight: 800; font-size: 1.05rem; color: #0f172a; line-height: 1.25;}
.brand .by {font-size: .8rem; color: #64748b;}
section[data-testid="stSidebar"] div[role="radiogroup"] {gap: 6px;}
section[data-testid="stSidebar"] div[role="radiogroup"] > label {
    padding: 11px 14px; border-radius: 10px; width: 100%; cursor: pointer;
    border: 1px solid transparent;}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {background: #eef2ff;}
section[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {display: none;}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
    background: #eef2ff; border: 1px solid #c7d2fe; color: #4338ca; font-weight: 700;}
.side-foot {font-size: .8rem; color: #64748b; margin-top: 26px; line-height: 1.6;}
.side-foot a {color: #4f46e5; text-decoration: none; font-weight: 600;}

/* ---------- hero ---------- */
.hero {background: linear-gradient(120deg, #4f46e5 0%, #2563eb 55%, #0ea5e9 100%);
       border-radius: 18px; padding: 30px 34px; color: #ffffff; margin-bottom: 22px;
       box-shadow: 0 10px 28px rgba(79,70,229,.25);}
.hero h1 {font-size: 2rem; margin: 0 0 8px 0; padding: 0; color: #ffffff; font-weight: 800; letter-spacing: -0.4px;}
.hero p {color: #e0e7ff; font-size: 1rem; margin: 0 0 14px 0; line-height: 1.55;}
.chip {display: inline-block; background: rgba(255,255,255,.18); border: 1px solid rgba(255,255,255,.3);
       color: #ffffff; padding: 5px 14px; border-radius: 999px; font-size: .8rem; margin: 4px 8px 0 0;}

/* ---------- cards ---------- */
.section-title {font-size: 1.05rem; font-weight: 700; color: #0f172a; margin: 2px 0 8px 0;}
.card {background: #ffffff; border: 1px solid #e5e7eb; border-radius: 14px; padding: 20px 22px;
       box-shadow: 0 4px 14px rgba(15,23,42,.05);}
.step .n {display: inline-flex; width: 30px; height: 30px; border-radius: 50%; background: #eef2ff;
          color: #4f46e5; font-weight: 800; align-items: center; justify-content: center; margin-bottom: 8px;}
.step .t {font-weight: 700; color: #0f172a; margin-bottom: 4px;}
.step .d {color: #475569; font-size: .92rem; line-height: 1.5;}

/* ---------- result ---------- */
.result {background: #ffffff; border: 1px solid #e5e7eb; border-top: 7px solid var(--c);
         border-radius: 16px; padding: 24px 26px; box-shadow: 0 10px 28px rgba(15,23,42,.08);}
.result .kicker {text-transform: uppercase; letter-spacing: 1.5px; font-size: .74rem; color: #64748b;}
.result .band {font-size: 2.6rem; font-weight: 800; color: var(--c); line-height: 1.1; margin: 4px 0 4px 0;}
.result .range {font-size: 1.05rem; color: #0f172a; font-weight: 700; margin-bottom: 4px;}
.result .sel {font-size: .85rem; color: #64748b; margin-bottom: 10px;}
.result .desc {color: #475569; font-size: .95rem; line-height: 1.5;}
.barrow {display: flex; align-items: center; margin: 12px 0;}
.barlabel {width: 76px; font-size: .9rem; color: #334155;}
.track {flex: 1; height: 12px; background: #e5e7eb; border-radius: 999px; overflow: hidden;}
.fill {height: 100%; border-radius: 999px;}
.pct {width: 56px; text-align: right; font-weight: 700; font-size: .9rem; color: #0f172a;}
.note {margin-top: 14px; padding: 10px 14px; background: #fffbeb; border: 1px solid #fcd34d;
       color: #92400e; border-radius: 10px; font-size: .88rem;}

/* ---------- help ---------- */
.info {background: #ffffff; border: 1px solid #e5e7eb; border-left: 6px solid #4f46e5;
       border-radius: 12px; padding: 18px 20px; margin-top: 12px;}
.info h4 {margin: 0 0 6px 0; color: #0f172a; font-size: 1.1rem;}
.info p {margin: 0 0 8px 0; color: #475569; line-height: 1.55; font-size: .95rem;}
.tag {display: inline-block; background: #eef2ff; color: #4338ca; border-radius: 999px;
      padding: 3px 12px; font-size: .8rem; font-weight: 600; margin: 2px 6px 2px 0;}
.bandcard {background: #ffffff; border: 1px solid #e5e7eb; border-top: 6px solid var(--c);
           border-radius: 12px; padding: 16px 18px;}
.bandcard .b {font-weight: 800; font-size: 1.3rem; color: var(--c);}
.bandcard .r {font-weight: 700; color: #0f172a; margin: 2px 0 6px 0;}
.bandcard .x {color: #475569; font-size: .9rem; line-height: 1.5;}
.footer {text-align: center; color: #64748b; font-size: .85rem; margin-top: 30px; padding-top: 16px;
         border-top: 1px solid #e5e7eb;}
.footer a {color: #4f46e5; text-decoration: none; font-weight: 600;}
"""
st.markdown("<style>" + CSS + "</style>", unsafe_allow_html=True)


@st.cache_resource
def load_assets():
    model = joblib.load("deal_size_model.joblib")
    with open("app_options.json") as f:
        opts = json.load(f)
    return model, opts


model, opts = load_assets()

BANDS = ["Small", "Medium", "Large"]
COLORS = {"Small": "#2563eb", "Medium": "#f59e0b", "Large": "#e11d48"}
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

# ---------- sidebar navigation ----------
with st.sidebar:
    st.markdown(
        '<div class="brand"><div class="logo">📊</div>'
        '<div class="name">Startup Deal-Size<br>Predictor</div>'
        f'<div class="by">by {AUTHOR}</div></div>',
        unsafe_allow_html=True,
    )
    page = st.radio("Navigate", ["📊  Predict", "📘  Help & Guide"], label_visibility="collapsed")
    st.markdown(
        f'<div class="side-foot">Trained on real Indian startup funding deals, 2015 to May 2022.<br><br>'
        f'<a href="{REPO}" target="_blank">View code on GitHub</a></div>',
        unsafe_allow_html=True,
    )


def hero(title, sub, chips=()):
    chip_html = "".join(f'<span class="chip">{c}</span>' for c in chips)
    st.markdown(f'<div class="hero"><h1>{title}</h1><p>{sub}</p>{chip_html}</div>', unsafe_allow_html=True)


def footer():
    st.markdown(
        f'<div class="footer">Built by <b>{AUTHOR}</b> &nbsp;·&nbsp; '
        f'<a href="{REPO}" target="_blank">GitHub</a><br>'
        "Educational project. Estimates come from historical data and are not financial advice.</div>",
        unsafe_allow_html=True,
    )


# =====================================================================
# PAGE 1: PREDICT
# =====================================================================
if page.startswith("📊"):
    hero("Predict the size of a funding round",
         "Describe a startup funding deal and get an estimate of how large it is likely to be, "
         "learned from real Indian startup deals.",
         ["4,300+ real deals", "2015 to May 2022", "Random Forest model"])

    left, right = st.columns([5, 6], gap="large")

    with left:
        with st.container(border=True):
            st.markdown('<div class="section-title">Describe the deal</div>', unsafe_allow_html=True)
            stage = st.selectbox("Funding stage", stages)
            sector = st.selectbox("Sector", opts["sectors"])
            city = st.selectbox("City", opts["cities"])
            year = st.slider("Year", opts["year_min"], opts["year_max"], opts["year_max"])
        st.caption("Not sure what an option means? Open **Help & Guide** from the menu.")

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

    st.markdown('<div class="section-title" style="margin-top:26px">How it works</div>', unsafe_allow_html=True)
    s1, s2, s3 = st.columns(3, gap="medium")
    steps = [
        ("1", "Choose the details", "Pick the funding stage, sector, city and year of a deal."),
        ("2", "The model compares", "It looks for similar deals among thousands of real past rounds."),
        ("3", "Get the size band", "You see whether such deals are usually Small, Medium or Large."),
    ]
    for col, (n, t, d) in zip((s1, s2, s3), steps):
        col.markdown(
            f'<div class="card step"><div class="n">{n}</div><div class="t">{t}</div><div class="d">{d}</div></div>',
            unsafe_allow_html=True,
        )
    footer()

# =====================================================================
# PAGE 2: HELP & GUIDE
# =====================================================================
else:
    hero("Help & Guide",
         "Click a tab to learn what each option means and how to read the result.")

    tabs = st.tabs(["Funding stage", "Sector", "City", "Year", "Size bands", "Reading the result"])

    with tabs[0]:
        st.write("A startup raises money in rounds. Pick a stage to see what it means.")
        pick = st.selectbox("Choose a stage", stages, key="help_stage")
        text, tend = STAGE_INFO.get(pick, ("A funding stage used in the dataset.", "Varies"))
        st.markdown(f'<div class="info"><h4>{pick}</h4><p>{text}</p>'
                    f'<span class="tag">{tend}</span></div>', unsafe_allow_html=True)
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
        cols = st.columns(3, gap="medium")
        info = {
            "Small": "Typical of the very first rounds, where a startup is just getting started.",
            "Medium": "Typical of growing startups that have a working product and customers.",
            "Large": "Typical of established companies raising big rounds to scale up.",
        }
        for col, b in zip(cols, BANDS):
            col.markdown(
                f'<div class="bandcard" style="--c:{COLORS[b]}"><div class="b">{b}</div>'
                f'<div class="r">{RANGE[b]}</div><div class="x">{info[b]}</div></div>',
                unsafe_allow_html=True,
            )

    with tabs[5]:
        st.markdown(
            '<div class="info"><h4>How to read the result</h4>'
            "<p><b>The big word</b> (Small, Medium or Large) is the size band the model thinks is most likely.</p>"
            "<p><b>The three bars</b> show how likely each band is. They add up to 100%.</p>"
            "<p><b>If one bar is much taller</b> than the others, the model is fairly sure. "
            "If the bars are close, the model is unsure and the answer is only a rough guide.</p>"
            "<p><b>What it cannot do:</b> it does not know a company's name, product, revenue or team, "
            "so it cannot say how much one specific startup will raise. It estimates the typical size "
            "of a round with this profile.</p></div>",
            unsafe_allow_html=True,
        )
    footer()
