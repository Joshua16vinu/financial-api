import streamlit as st
import pandas as pd
import plotly.express as px

from kite_api import get_login_url, generate_access_token, get_positions
from fmp_api import get_historical_data, get_company_info
from mf_api import get_mutual_fund_data
from ai_agent import ai_portfolio_insights, ai_chat

st.set_page_config(page_title="Smart Financial Assistant", layout="wide")
st.title("💹 Smart Financial Assistant")

# --- SIDEBAR: Kite Authentication ---
st.sidebar.header("🔑 Kite Connect Authentication")

if "access_token" not in st.session_state:
    st.session_state["access_token"] = None

if st.sidebar.button("Open Kite Login URL"):
    login_url = get_login_url()
    if "Error" not in login_url:
        st.sidebar.markdown(f"[Click here to login]({login_url})")
    else:
        st.sidebar.error(login_url)

request_token_input = st.sidebar.text_input("Paste your Request Token:")

if st.sidebar.button("Generate Access Token") and request_token_input:
    token = generate_access_token(request_token_input)
    if "Error" in token:
        st.sidebar.error(token)
    else:
        st.sidebar.success("Access Token generated successfully!")

menu = st.sidebar.radio("Navigate", ["Stock Data", "Mutual Funds", "Portfolio (Kite)", "AI Insights", "Chat"])

# --- STOCK DATA (FMP API) ---
if menu == "Stock Data":
    st.header("📈 Stock Overview (via FMP)")
    symbol = st.text_input("Enter NSE Symbol (e.g., RELIANCE):", "RELIANCE")

    if st.button("Fetch Stock Data"):
        st.subheader("Company Information")
        info = get_company_info(symbol + ".NS")
        if info:
            st.write(info)
        else:
            st.warning("No company info available.")

        st.subheader("Historical Price Trend (6 Months)")
        df = get_historical_data(symbol + ".NS")
        if not df.empty:
            fig = px.line(df, x=df.index, y="close", title=f"{symbol} - Last 6 Months")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No historical data available.")

# --- MUTUAL FUND SECTION ---
elif menu == "Mutual Funds":
    st.header("💼 Mutual Fund Insights")
    st.info("Select a popular fund or enter a scheme code below.")

    popular_funds = {
        "Quant Small Cap Fund": "120828",
        "Parag Parikh Flexi Cap Fund": "118834",
        "Axis Bluechip Fund": "120465",
        "SBI Small Cap Fund": "118834",
        "HDFC Mid-Cap Opportunities Fund": "119551"
    }

    col1, col2 = st.columns([2, 1])
    with col1:
        fund_name = st.selectbox("Choose from popular funds:", list(popular_funds.keys()))
    with col2:
        scheme_code = st.text_input("Or enter a mutual fund code manually:", "")

    if not scheme_code:
        scheme_code = popular_funds[fund_name]

    if st.button("Fetch Fund"):
        mf = get_mutual_fund_data(scheme_code)
        if "error" in mf:
            st.error(mf["error"])
        else:
            st.markdown(f"""
            ### 🏦 {mf['fund_name']}
            **Fund House:** {mf['fund_house']}  
            **Category:** {mf['category']}  
            ⭐ **Rating:** {mf['rating']}  
            📈 **Risk:** {mf['risk']}  
            💰 **Expense Ratio:** {mf['expense_ratio']}  
            🏦 **AUM:** {mf['aum']}  
            💵 **Dividend Info:** {mf['dividend_info']}  
            """)

            if not mf["nav_df"].empty:
                st.subheader("📊 NAV Trend (Last 30 Days)")
                st.line_chart(mf["nav_df"].set_index("date")["nav"])
            else:
                st.warning("No NAV data available for this scheme.")

# --- PORTFOLIO (Kite API Positions) ---
elif menu == "Portfolio (Kite)":
    st.header("📊 Your Live Portfolio (Kite Positions)")
    if "access_token" not in st.session_state or not st.session_state["access_token"]:
        st.warning("Please generate Kite access token first.")
    else:
        positions = get_positions()
        st.dataframe(positions)

# --- AI INSIGHTS ---
elif menu == "AI Insights":
    st.header("🧠 AI Portfolio Insights")
    if st.button("Generate Insights"):
        insights = ai_portfolio_insights("current portfolio holdings")
        st.write(insights)

# --- CHAT ---
else:
    st.header("💬 Chat with Financial Assistant")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_query = st.text_input("Ask your question:")
    if st.button("Send") and user_query.strip():
        response = ai_chat(user_query)
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.markdown(f"**You:** {user_query}")
        st.markdown(f"**Assistant:** {response}")
