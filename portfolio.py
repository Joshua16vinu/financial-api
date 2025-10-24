import pandas as pd
import streamlit as st
from kite_api import get_holdings, get_positions
from fmp_api import get_historical_data

# -----------------------------
# 🧠 Utility: Calculate value from holdings/positions
# -----------------------------
def calculate_value(items):
    """
    Calculate total value from a list of holdings or positions using FMP live prices.
    """
    total_value = 0
    data = []

    for item in items:
        symbol = item.get("symbol") or item.get("tradingsymbol")
        qty = item.get("quantity", 0)

        if not symbol:
            continue

        try:
            price_df = get_historical_data(symbol)
            last_price = price_df["close"].iloc[-1] if not price_df.empty else 0.0
        except Exception as e:
            st.warning(f"Error fetching price for {symbol}: {e}")
            last_price = 0.0

        value = qty * last_price
        total_value += value

        data.append({
            "Symbol": symbol,
            "Quantity": qty,
            "Last Price (₹)": round(last_price, 2),
            "Value (₹)": round(value, 2),
        })

    return total_value, pd.DataFrame(data)


# -----------------------------
# 📊 Show Portfolio Summary in Streamlit
# -----------------------------
def show_portfolio_summary():
    """
    Display holdings, positions, and combined portfolio summary.
    """
    st.subheader("💹 Portfolio Analyzer")

    try:
        holdings = get_holdings()
        positions = get_positions()
    except Exception as e:
        st.error(f"Error fetching portfolio data: {e}")
        return

    # Ensure lists
    holdings = holdings if isinstance(holdings, list) else [holdings]
    positions = positions if isinstance(positions, list) else [positions]

    total_hold_value, holdings_df = calculate_value(holdings)
    total_pos_value, positions_df = calculate_value(positions)
    total_portfolio_value = total_hold_value + total_pos_value

    # -----------------------------
    # Tabs for clean UI
    # -----------------------------
    tab1, tab2, tab3 = st.tabs(["Holdings", "Positions", "Summary"])

    with tab1:
        st.metric("Total Holdings Value (₹)", f"{total_hold_value:,.2f}")
        if not holdings_df.empty:
            st.dataframe(holdings_df, use_container_width=True)
        else:
            st.info("No holdings found.")

    with tab2:
        st.metric("Total Positions Value (₹)", f"{total_pos_value:,.2f}")
        if not positions_df.empty:
            st.dataframe(positions_df, use_container_width=True)
        else:
            st.info("No open positions.")

    with tab3:
        st.metric("Total Portfolio Value (₹)", f"{total_portfolio_value:,.2f}")
        st.caption("💡 Includes both holdings and positions with live FMP prices.")
