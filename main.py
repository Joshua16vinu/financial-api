import streamlit as st
import pandas as pd
import plotly.express as px
from kite_api import get_live_quote, get_login_url, generate_access_token
# from yfinance_api import get_historical_data, get_company_info
from fmp_api import get_historical_data, get_company_info
from mf_api import get_mutual_fund_data
from portfolio import portfolio, get_portfolio_value
from ai_agent import ai_portfolio_insights, ai_chat

st.set_page_config(page_title="Smart Financial Assistant", layout="wide")
st.title("💰 Financial Assistant Dashboard")

# --- Kite Connect Authentication ---
st.sidebar.header("🔑 Kite Connect Auth")
if "access_token" not in st.session_state:
    st.session_state["access_token"] = None

st.sidebar.markdown("1️⃣ Click login and paste request token:")
if st.sidebar.button("Open Kite Login URL"):
    st.write(f"[Click here to login]({get_login_url()})")

request_token_input = st.sidebar.text_input("Paste Request Token here:")
if st.sidebar.button("Generate Access Token") and request_token_input:
    token = generate_access_token(request_token_input)
    if "Error" in token:
        st.error(token)
    else:
        st.session_state["access_token"] = token
        st.success("Access Token generated successfully!")

menu = st.sidebar.radio("Select Section", ["Stock Data", "Mutual Funds", "Portfolio", "AI Insights", "Chat"])

# --- STOCK DATA ---
if menu == "Stock Data":
    st.header("📈 Stock Overview")
    symbol = st.text_input("Enter NSE Symbol (e.g., RELIANCE)", "RELIANCE")
    if st.button("Fetch Data"):
        # Fetch live quote only if access token exists
        if st.session_state.get("access_token"):
            live = get_live_quote(symbol)
            if isinstance(live, str) and live.startswith("Error"):
                st.error(live)
            else:
                st.metric(label=f"Live Price of {symbol}", value=f"₹{live}")
        else:
            st.warning("Generate Kite Access Token first in sidebar!")

        info = get_company_info(symbol + ".NS")
        st.subheader("Company Information")
        st.write(info)

        data = get_historical_data(symbol + ".NS", period="6mo")
        st.subheader("Price Trend")
        fig = px.line(data, x=data.index, y="close", title=f"{symbol} - Last 6 Months")
        st.plotly_chart(fig, use_container_width=True)

# --- MUTUAL FUNDS ---
elif menu == "Mutual Funds":
    st.header("💼 Mutual Fund Insights")
    scheme = st.text_input("Enter Mutual Fund Code (e.g., 120828)", "120828")
    if st.button("Fetch Fund"):
        mf = get_mutual_fund_data(scheme)
        if "error" in mf:
            st.error(mf["error"])
        else:
            st.write(f"**{mf['fund_name']}**  \n🏦 {mf['fund_house']}  \n📊 Category: {mf['category']}")
            st.write(f"⭐ Rating: {mf['rating']}")
            st.write(f"📈 Risk: {mf['risk']}")
            st.write(f"💰 Expense Ratio: {mf['expense_ratio']}")
            st.write(f"🏦 AUM: {mf['aum']}")
            st.write(f"💵 Dividend Info: {mf['dividend_info']}")
            
# Plot NAV chart
            nav_df = mf["nav_df"]
            nav_df["nav"] = nav_df["nav"].astype(float)
            nav_df["date"] = pd.to_datetime(nav_df["date"], dayfirst=True)  # <-- fixed
            st.line_chart(nav_df.set_index("date")["nav"])


# --- PORTFOLIO ---
elif menu == "Portfolio":
    st.header("📊 Portfolio Summary (Stocks + MFs)")
    st.info("Simulated unified view combining stock and mutual fund data.")
    df_list, total_value = get_portfolio_value(portfolio)
    df = pd.DataFrame(df_list)
    st.dataframe(df)
    st.success(f"💵 Total Portfolio Value: ₹{total_value:,.2f}")

# --- AI INSIGHTS ---
elif menu == "AI Insights":
    st.header("🧠 AI Portfolio Insights")
    if st.button("Get Insights"):
        insights = ai_portfolio_insights(portfolio)
        st.write(insights)

# --- CHAT INTERFACE ---
else:
    st.header("💬 Chat with Your Financial Agent")
    user_query = st.text_input("Ask me anything about your portfolio:")
    if st.button("Send"):
        response = ai_chat(user_query, context=str(portfolio))
        st.write(response)