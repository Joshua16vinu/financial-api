import streamlit as st
import pandas as pd
import requests

# --- Fetch Data ---
def get_mutual_fund_data(scheme_code="120828"):
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    res = requests.get(url).json()
    meta = res.get("meta", {})
    navs = res.get("data", [])[:30]

    nav_df = pd.DataFrame(navs)
    nav_df["date"] = pd.to_datetime(nav_df["date"], format="%d-%m-%Y", errors="coerce")
    nav_df["nav"] = pd.to_numeric(nav_df["nav"], errors="coerce")

    return {
        "fund_name": meta.get("scheme_name", "Unknown Fund"),
        "fund_house": meta.get("fund_house", "Unknown AMC"),
        "category": meta.get("scheme_category", "N/A"),
        "nav_df": nav_df
    }

# --- Streamlit UI ---
st.header("💼 Mutual Fund Insights")

# Popular fund options for convenience
popular_funds = {
    "Quant Small Cap Fund": "120828",
    "Parag Parikh Flexi Cap Fund": "118834",
    "Axis Bluechip Fund": "120465",
    "SBI Small Cap Fund": "118834",
    "HDFC Mid-Cap Opportunities Fund": "119551"
}

fund_name = st.selectbox("Choose a Mutual Fund", options=list(popular_funds.keys()))
scheme_code = popular_funds[fund_name]

if st.button("Fetch Fund Data"):
    mf = get_mutual_fund_data(scheme_code)

    st.markdown(f"""
    ### 🏦 {mf['fund_name']}
    **Fund House:** {mf['fund_house']}  
    **Category:** {mf['category']}
    """)

    if not mf["nav_df"].empty:
        st.subheader("📈 NAV Trend (Last 30 Days)")
        st.line_chart(mf["nav_df"].set_index("date")["nav"])
    else:
        st.warning("No NAV data available.")
