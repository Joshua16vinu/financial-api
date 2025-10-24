import streamlit as st
import pandas as pd
import requests
from kite_api import get_holdings, get_positions  # Updated kite_api integration
from fmp_api import BASE_URL, FMP_API_KEY  # reuse same constants

st.set_page_config(page_title="Portfolio Analyzer", layout="wide")

# --- Helper: Get Live Price from FMP ---
def get_live_price(symbol):
    """Fetch latest price from FMP"""
    try:
        url = f"{BASE_URL}/quote/{symbol}?apikey={FMP_API_KEY}"
        res = requests.get(url).json()
        if res and len(res) > 0:
            return res[0].get("price", None)
    except Exception as e:
        st.warning(f"Error fetching price for {symbol}: {e}")
    return None


# --- Fetch Data from Kite API ---
st.title("📊 Portfolio Analyzer")

with st.spinner("Fetching holdings and positions from Zerodha..."):
    try:
        holdings = get_holdings()
        positions = get_positions()
    except Exception as e:
        st.error(f"Error fetching data from Kite API: {e}")
        holdings, positions = [], []


# --- Display Holdings ---
st.subheader("💼 Holdings")

if holdings:
    holdings_df = pd.DataFrame(holdings)

    # Add live price & PnL calculations
    prices, current_values, pnls = [], [], []
    for _, row in holdings_df.iterrows():
        symbol = row.get("tradingsymbol")
        qty = float(row.get("quantity", 0))
        avg_price = float(row.get("average_price", 0))
        live_price = get_live_price(symbol)
        prices.append(live_price)
        if live_price:
            current_value = live_price * qty
            pnl = (live_price - avg_price) * qty
        else:
            current_value, pnl = None, None
        current_values.append(current_value)
        pnls.append(pnl)

    holdings_df["Live Price"] = prices
    holdings_df["Current Value"] = current_values
    holdings_df["Unrealized P&L"] = pnls

    total_value = holdings_df["Current Value"].sum(skipna=True)
    total_pnl = holdings_df["Unrealized P&L"].sum(skipna=True)

    st.dataframe(
        holdings_df[["tradingsymbol", "quantity", "average_price", "Live Price", "Current Value", "Unrealized P&L"]],
        use_container_width=True
    )

    st.metric(label="Total Portfolio Value", value=f"₹{total_value:,.2f}")
    st.metric(label="Total Unrealized P&L", value=f"₹{total_pnl:,.2f}")

else:
    st.info("No holdings found.")


# --- Display Positions ---
st.subheader("📈 Open Positions")

if positions:
    positions_df = pd.DataFrame(positions)

    # Add live prices for open positions
    prices, mtm_list = [], []
    for _, row in positions_df.iterrows():
        symbol = row.get("tradingsymbol")
        net_qty = float(row.get("quantity", 0))
        avg_price = float(row.get("average_price", 0))
        live_price = get_live_price(symbol)
        prices.append(live_price)
        mtm = (live_price - avg_price) * net_qty if live_price else None
        mtm_list.append(mtm)

    positions_df["Live Price"] = prices
    positions_df["MTM"] = mtm_list

    st.dataframe(
        positions_df[["tradingsymbol", "quantity", "average_price", "Live Price", "MTM"]],
        use_container_width=True
    )

    total_mtm = positions_df["MTM"].sum(skipna=True)
    st.metric(label="Total MTM (Positions)", value=f"₹{total_mtm:,.2f}")

else:
    st.info("No open positions found.")


st.caption("💡 Data fetched from Zerodha API (holdings & positions) and live prices from Financial Modeling Prep (FMP).")
