import json
import joblib
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Startup Deal-Size Predictor", page_icon="📊", layout="centered")

REPO = "https://github.com/RituPrabhat/indian-startup-funding-analysis"
AUTHOR = "Ritu Prabhat"

CSS = """
#MainMenu, footer {visibility: hidden;}
.block-container {max-width: 880px; padding-top: 1.5rem; padding-bottom: 3rem;}
.hero {background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 55%, #4f46e5 100%);
       border-radius: 18px; padding: 34px 36px; color: #ffffff; margin-bottom: 22px;
       box-shadow: 0 10px 30px rgba(15,23,42,.35);}
.hero h1 {font-size: 2.1rem; margin: 0 0 8px 0; padding: 0; color: #ffffff;
          font-weight: 800; letter-spacing: -0.5px;}
.hero p {color: #cbd5e1; font-size: 1.02rem; margin: 0 0 16px 0; line-height: 1.55;}
.chip {display: inline-block; background: rgba(255,255,255,.12);
       border: 1px solid rgba(255,255,255,.22); color: #ffffff; padding: 6px 14px;
       border-radius: 999px; font-size: .82rem; margin: 4px 8px 0 0;}
.section-title {font-size: 1.1rem; font-weight: 700; margin: 2px 0 10px 0;}
div.stButton > button {border-radius: 10px;}
.result {border-radius: 16px; padding: 26px 28px; margin-top: 18px; color: #f9fafb;
         background: linear-gradient(135deg, #111827, #1f2937);
         border-left: 8px solid var(--c); box-shadow: 0 8px 24px rgba(0,0,0,.3);}
.result .kicker {text-transform: uppercase; letter-spacing: 1.5px; font-size: .75rem; color: #9ca3af;}
.result .band {font-size: 2.5rem; font-weight: 800; color: var(--c); line-height: 1.1; margin: 4px 0 6px 0;}
.result .range {font-size: 1.05rem; color: #e5e7eb; margin-bottom: 6px; font-weight: 600;}
.result .sel {font-size: .85rem; color: #9ca3af; margin-bottom: 8px;}
.result .desc {color: #cbd5e1; font-size: .95rem; line-height: 1.5;}
.barrow {display: flex; align-items: center; margin: 12px 0;}
.barlabel {width: 76px; font-size: .9rem; color: #e5e7eb;}
.track {flex: 1; height: 12px; background: rgba(255,255,255,.1); border-radius: 999px; overflow: hidden;}
.fill {height: 100%; border-radius: 999px;}
.pct {width: 56px; text-align: right; font-weight: 700; font-size: .9rem; color: #f9fafb;}
.note {margin-top: 14px; padding: 10px 14px; background: rgba(251,191,36,.12);
       border: 1px solid rgba(251,191,36,.35); color: #fde68a; border-radius: 10px; font-size: .88rem;}
.footer {text-align: center; color: #9ca3af; font-size: .85rem; margin-top: 34px;
         padding-top: 18px; border-top: 1px solid rgba(128,128,128,.25);}
.footer a {color: #818cf8; text-decoration: none;}
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
COLORS = {"Small": "#4C9BE8", "Medium": "#F2A93B", "Large": "#E4572E"}
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

# ---------- Hero ----------
st.markdown(
    '<div class="hero">'
    "<h1>Indian Startup Deal-Size Predictor</h1>"
    "<p>Describe a funding round and get an estimate of how large it is likely to be, "
    "learned from real Indian startup deals.</p>"
    '<span class="chip">4,300+ real deals</span>'
    '<span class="chip">2015 to May 2022</span>'
    '<span class="chip">Random Forest model</span>'
    "</div>",
    unsafe_allow_html=True,
)

# ---------- Inputs ----------
with st.container(border=True):
    st.markdown('<div class="section-title">Describe the deal</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        stage = st.selectbox("Funding stage", stages)
        sector = st.selectbox("Sector", opts["sectors"])
    with c2:
        city = st.selectbox("City", opts["cities"])
        year = st.slider("Year", opts["year_min"], opts["year_max"], opts["year_max"])

# ---------- Prediction ----------
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
    note = ('<div class="note">The probabilities are close together, so the model is '
            "not very sure about this one. Treat it as a rough estimate.</div>")

st.markdown(
    f'<div class="result" style="--c:{COLORS[best]}">'
    '<div class="kicker">Predicted deal size</div>'
    f'<div class="band">{best}</div>'
    f'<div class="range">{RANGE[best]}</div>'
    f'<div class="sel">{stage} &nbsp;·&nbsp; {sector} &nbsp;·&nbsp; {city} &nbsp;·&nbsp; {year}</div>'
    f'<div class="desc">{DESC[best]}</div>'
    f'<div style="margin-top:16px">{bars}</div>'
    f"{note}"
    "</div>",
    unsafe_allow_html=True,
)

# ---------- Help ----------
with st.expander("How to read this"):
    st.write(
        "The model looks at four details of a deal (funding stage, sector, city and year) "
        "and compares them with thousands of past Indian startup deals. The bars show how "
        "likely each size band is, and the tallest one is the prediction."
    )
    st.write(
        "It estimates the **typical size of a round like this**. It does not know a company's "
        "name, product, revenue or team, so it cannot say how much one specific startup will raise."
    )

