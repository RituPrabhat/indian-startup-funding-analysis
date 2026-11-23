import json
import joblib
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Startup Deal-Size Predictor", page_icon="📊")


@st.cache_resource
def load_assets():
    model = joblib.load("deal_size_model.joblib")
    with open("app_options.json") as f:
        opts = json.load(f)
    return model, opts


model, opts = load_assets()

st.title("📊 Indian Startup Deal-Size Predictor")
st.write(
    "Pick the details of a funding deal and the model predicts whether it is "
    "**Small** (under $1M), **Medium** ($1M–$10M) or **Large** (over $10M)."
)

col1, col2 = st.columns(2)
with col1:
    stage = st.selectbox("Funding stage", opts["stages"])
    sector = st.selectbox("Sector", opts["sectors"])
with col2:
    city = st.selectbox("City", opts["cities"])
    year = st.slider("Year", opts["year_min"], opts["year_max"], opts["year_max"])

if st.button("Predict deal size", type="primary"):
    row = pd.DataFrame(
        [{"Sector": sector, "City_Group": city, "Stage_Std": stage, "Year": year}]
    )
    proba = pd.Series(model.predict_proba(row)[0], index=model.classes_)
    proba = proba[["Small", "Medium", "Large"]]
    best = proba.idxmax()

    st.subheader(f"Predicted band: {best}")
    st.write(f"Confidence: {proba.max():.0%}")
    st.bar_chart(proba)

st.divider()
st.caption(
    "Model: Random Forest trained on ~4,300 Indian startup deals (2015 to May 2022) "
    "with a known amount. Test accuracy about 62% (a majority-class guess gets 43%). "
    "Funding stage is the strongest signal; sector and city add little. "
    "This is an educational project, not financial advice."
)
