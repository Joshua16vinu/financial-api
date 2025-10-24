import streamlit as st
import pandas as pd
import plotly.express as px

from kite_api import (
    get_live_quote, get_login_url, generate_access_token,
    get_positions, get_holdings, get_funds,
    place_order, create_gtt, list_gtt_orders,
    create_alert, get_alerts, get_margin_requirements
)
from fmp_api import get_historical_data, get_company_info
from mf_api import get_mutual_fund_data
from portfolio import show_portfolio_summary
from ai_agent import ai_portfolio_insights, ai_chat

st.set_page_config(page_title="Smart Financial Assistant", layout="wide")
st.title("💰 Financial Assistant Dashboard")

# -----------------------------
# Kite Connect Authentication
# -----------------------------
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

# -----------------------------
# Sidebar Menu
# -----------------------------
menu = st.sidebar.radio("Select Section", [
    "Stock Data", "Mutual Funds", "Portfolio", "AI Insights", "Chat", "Kite Tools"
])

# -----------------------------
# STOCK DATA
# -----------------------------
if menu == "Stock Data":
    st.header("📈 Stock Overview")
    symbol = st.text_input("Enter NSE Symbol (e.g., RELIANCE)", "RELIANCE")
    if st.button("Fetch Data"):
        live = get_live_quote(symbol)
        st.metric(label=f"Live Price of {symbol}", value=f"₹{live}")

        info = get_company_info(symbol + ".NS")
        st.subheader("Company Information")
        st.write(info)

        data = get_historical_data(symbol + ".NS", period="6mo")
        st.subheader("Price Trend")
        fig = px.line(data, x=data.index, y="close", title=f"{symbol} - Last 6 Months")
        st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# MUTUAL FUNDS
# -----------------------------
elif menu == "Mutual Funds":
    st.header("💼 Mutual Fund Insights")
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

# -----------------------------
# PORTFOLIO
# -----------------------------
elif menu == "Portfolio":
    show_portfolio_summary()

# -----------------------------
# AI INSIGHTS
# -----------------------------
elif menu == "AI Insights":
    st.header("🧠 AI Portfolio Insights")
    if st.button("Get Insights"):
        insights = ai_portfolio_insights()
        st.write(insights)

# -----------------------------
# CHAT
# -----------------------------
elif menu == "Chat":
    st.header("💬 Chat with Your Financial Agent")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_query = st.text_input("Ask me anything about your portfolio:")
    if st.button("Send") and user_query.strip():
        response = ai_chat(user_query)
        st.markdown(f"**🧑‍💼 You:** {user_query}")
        st.markdown(f"**🤖 Assistant:** {response}")

# -----------------------------
# KITE TOOLS
# -----------------------------
elif menu == "Kite Tools":
    st.header("🪁 Zerodha Kite Tools")
    st.info("Manage orders, positions, GTTs, margins, and alerts directly here.")
    # Tabs: Place Order, Positions, GTT, Alerts, Margins
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Place Order", "Positions", "GTT Orders", "Alerts", "Margins"])

    # --- Place Order
    with tab1:
        st.subheader("📤 Place Order")
        symbol = st.text_input("Symbol (e.g., RELIANCE)")
        qty = st.number_input("Quantity", 1, 1000, 1)
        order_type = st.selectbox("Order Type", ["MARKET", "LIMIT"])
        trans_type = st.selectbox("Transaction", ["BUY", "SELL"])
        price = st.number_input("Price (for LIMIT orders)", 0.0)
        if st.button("Submit Order"):
            res = place_order(symbol, qty, order_type, trans_type, price)
            st.write(res)

    # --- Positions & Holdings
    with tab2:
        st.subheader("📊 Positions & Holdings")
        st.write(get_positions())
        st.write(get_holdings())
        st.write(get_funds())

    # --- GTT Orders
    with tab3:
        st.subheader("📆 Manage GTT Orders")
        sym = st.text_input("Symbol for GTT")
        trg_price = st.number_input("Trigger Price", 0.0)
        qty = st.number_input("Quantity", 1)
        if st.button("Create GTT"):
            res = create_gtt(sym, trg_price, qty)
            st.write(res)
        st.write("Existing GTT Orders:")
        st.json(list_gtt_orders())

    # --- Alerts
    with tab4:
        st.subheader("⏰ Price Alerts")
        sym = st.text_input("Alert Symbol")
        alert_price = st.number_input("Alert Price", 0.0)
        note = st.text_input("Note", "Price Alert")
        if st.button("Add Alert"):
            st.success(create_alert(sym, alert_price, note))
        st.write(get_alerts())

    # --- Margins
    with tab5:
        st.subheader("💰 Margin Requirement Check")
        sym = st.text_input("Symbol for Margin Check", "RELIANCE")
        qty = st.number_input("Quantity for Margin", 1)
        res = get_margin_requirements(sym, qty)
        st.json(res)
