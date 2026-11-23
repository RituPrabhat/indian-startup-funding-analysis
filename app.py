import json
import joblib
import pandas as pd
import altair as alt
import streamlit as st

st.set_page_config(page_title="Startup Deal-Size Predictor", page_icon="📊", layout="centered")


@st.cache_resource
def load_assets():
    model = joblib.load("deal_size_model.joblib")
    with open("app_options.json") as f:
        opts = json.load(f)
    return model, opts


model, opts = load_assets()

BANDS = ["Small", "Medium", "Large"]
COLORS = ["#4C9BE8", "#F2A93B", "#E4572E"]
MEANING = {
    "Small": "Deals with this profile are usually **under $1M**, typical of very early rounds.",
    "Medium": "Deals with this profile are usually **between $1M and $10M**.",
    "Large": "Deals with this profile are usually **above $10M**, typical of later, bigger rounds.",
}

# show stages in their natural order instead of alphabetical
STAGE_ORDER = ["Pre-Seed", "Seed/Angel", "Pre-Series A/B", "Series A", "Series B",
               "Series C", "Series D+", "Private Equity", "Unknown/Other"]
stages = [s for s in STAGE_ORDER if s in opts["stages"]]
stages += [s for s in opts["stages"] if s not in stages]

st.title("📊 Indian Startup Deal-Size Predictor")
st.caption("A machine learning model trained on about 4,300 real Indian startup funding deals (2015 to May 2022).")

tab1, tab2, tab3 = st.tabs(["Predict", "Model performance", "About"])

# ---------------- TAB 1 ----------------
with tab1:
    st.write(
        "Choose the details of a funding deal. The model predicts whether the round is "
        "**Small** (under $1M), **Medium** ($1M to $10M) or **Large** (over $10M)."
    )

    c1, c2 = st.columns(2)
    with c1:
        stage = st.selectbox("Funding stage", stages)
        sector = st.selectbox("Sector", opts["sectors"])
    with c2:
        city = st.selectbox("City", opts["cities"])
        year = st.slider("Year", opts["year_min"], opts["year_max"], opts["year_max"])

    if st.button("Predict deal size", type="primary"):
        row = pd.DataFrame([{"Sector": sector, "City_Group": city,
                             "Stage_Std": stage, "Year": year}])
        proba = pd.Series(model.predict_proba(row)[0], index=model.classes_)[BANDS]
        best = proba.idxmax()

        st.subheader(f"Predicted band: {best}")
        st.write(MEANING[best])

        m1, m2, m3 = st.columns(3)
        for col, band in zip((m1, m2, m3), BANDS):
            col.metric(band, f"{proba[band]:.0%}")

        df = pd.DataFrame({"Band": BANDS, "Probability": proba.values})
        chart = (
            alt.Chart(df)
            .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
            .encode(
                x=alt.X("Band:N", sort=BANDS, axis=alt.Axis(labelAngle=0, title=None)),
                y=alt.Y("Probability:Q", scale=alt.Scale(domain=[0, 1]),
                        axis=alt.Axis(format="%", title="Probability")),
                color=alt.Color("Band:N", scale=alt.Scale(domain=BANDS, range=COLORS), legend=None),
                tooltip=["Band", alt.Tooltip("Probability:Q", format=".0%")],
            )
            .properties(height=300)
        )
        st.altair_chart(chart)

        if proba.max() < 0.5:
            st.warning("The model is not very sure here: the probabilities are spread across "
                       "the bands, so treat this as a rough guess.")
        st.caption("The model uses only stage, sector, city and year. It cannot see a company's "
                   "name, product, revenue or team.")

# ---------------- TAB 2 ----------------
with tab2:
    st.subheader("How well does it work?")
    st.write("Scores on 867 deals the model never saw during training:")
    st.table(pd.DataFrame({
        "Model": ["Always guess 'Medium' (baseline)", "Logistic Regression", "Random Forest (used here)"],
        "Accuracy": ["42.7%", "58.8%", "62.3%"],
        "Macro-F1": ["0.20", "0.59", "0.63"],
    }).set_index("Model"))

    st.subheader("Where does it get things right and wrong?")
    st.table(pd.DataFrame(
        [[153, 75, 11], [104, 183, 83], [27, 27, 204]],
        index=["True Large", "True Medium", "True Small"],
        columns=["Predicted Large", "Predicted Medium", "Predicted Small"],
    ))
    st.write(
        "- Small deals are easiest to spot, and Large deals are decent.\n"
        "- Medium is hardest, because it sits between the other two bands.\n"
        "- Mistakes are mostly between neighbouring bands. Calling a Large deal Small is rare."
    )

    st.subheader("What drives the prediction?")
    st.write("**Funding stage** is by far the strongest signal (Seed/Angel rounds are mostly small). "
             "Year comes next. Sector and city add little.")

    st.subheader("Limitations")
    st.write(
        "- Trained only on deals that disclosed an amount (about 74% of the data).\n"
        "- Random train/test split, not split by time, so the real-world score may be lower.\n"
        "- The $1M and $10M band limits are a choice, not a rule.\n"
        "- Covers 2015 to May 2022 only."
    )

# ---------------- TAB 3 ----------------
with tab3:
    st.subheader("About this project")
    st.write(
        "This app is the last step of an end-to-end data project: merging three public "
        "datasets, cleaning them, analysing them with SQL and Python, building a Power BI "
        "dashboard, then training and deploying this model."
    )
    st.write("**Built by:** Ritu Prabhat")
    st.write("**Code, notebooks and data credits:** "
             "[GitHub repository](https://github.com/RituPrabhat/indian-startup-funding-analysis)")
    st.caption("Educational project, not financial advice.")
