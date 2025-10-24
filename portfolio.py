import streamlit as st
import pandas as pd
from kite_api import get_holdings, get_positions
from fmp_api import get_latest_price  # ✅ FMP fallback added
from fmp_api import get_historical_data  # optional for insights

# --- Portfolio Display ---
def show_portfolio_summary():
    st.title("📈 Portfolio Analyzer")

    tabs = st.tabs(["Holdings", "Positions", "Summary"])

    # --- Tab 1: Holdings ---
    with tabs[0]:
        st.subheader("Holdings")

        try:
            holdings = get_holdings() or []
        except Exception as e:
            st.error(f"Error fetching holdings: {e}")
            holdings = []

        if not isinstance(holdings, list):
            holdings = [holdings]

        if not holdings:
            st.info("No holdings found.")
        else:
            data = []
            for h in holdings:
                symbol = h.get("tradingsymbol") or h.get("symbol")
                qty = h.get("quantity", 0)
                last_price = h.get("last_price", 0) or 0

                # ✅ fallback via FMP
                if not last_price or last_price == 0:
                    last_price = get_latest_price(symbol)

                value = qty * last_price
                data.append({
                    "Symbol": symbol,
                    "Quantity": qty,
                    "Last Price (₹)": round(last_price, 2),
                    "Value (₹)": round(value, 2),
                })

            df = pd.DataFrame(data)
            total_value = df["Value (₹)"].sum()

            st.metric("Total Holdings Value (₹)", f"{total_value:,.2f}")
            st.dataframe(df, use_container_width=True)

    # --- Tab 2: Positions ---
    with tabs[1]:
        st.subheader("Positions")

        try:
            positions = get_positions() or []
        except Exception as e:
            st.error(f"Error fetching positions: {e}")
            positions = []

        if not isinstance(positions, list):
            positions = [positions]

        if not positions:
            st.info("No positions found.")
        else:
            data = []
            for p in positions:
                symbol = p.get("tradingsymbol") or p.get("symbol")
                qty = p.get("quantity", 0)
                last_price = p.get("last_price", 0) or 0

                # ✅ fallback via FMP
                if not last_price or last_price == 0:
                    last_price = get_latest_price(symbol)

                value = qty * last_price
                data.append({
                    "Symbol": symbol,
                    "Quantity": qty,
                    "Last Price (₹)": round(last_price, 2),
                    "Value (₹)": round(value, 2),
                })

            df = pd.DataFrame(data)
            total_value = df["Value (₹)"].sum()

            st.metric("Total Positions Value (₹)", f"{total_value:,.2f}")
            st.dataframe(df, use_container_width=True)

    # --- Tab 3: Summary ---
    with tabs[2]:
        st.subheader("Portfolio Summary")

        try:
            holdings = get_holdings() or []
            positions = get_positions() or []
        except Exception as e:
            st.error(f"Error fetching portfolio summary: {e}")
            return

        all_data = holdings + positions
        if not all_data:
            st.info("No portfolio data available.")
            return

        summary = []
        for item in all_data:
            symbol = item.get("tradingsymbol") or item.get("symbol")
            qty = item.get("quantity", 0)
            last_price = item.get("last_price", 0) or 0

            if not last_price or last_price == 0:
                last_price = get_latest_price(symbol)

            summary.append({
                "Symbol": symbol,
                "Quantity": qty,
                "Last Price (₹)": round(last_price, 2),
                "Value (₹)": round(qty * last_price, 2),
            })

        df = pd.DataFrame(summary)
        total_value = df["Value (₹)"].sum()

        st.metric("Total Portfolio Value (₹)", f"{total_value:,.2f}")
        st.dataframe(df, use_container_width=True)
