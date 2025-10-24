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

        if isinstance(holdings, dict):
            holdings = [holdings]

        if not holdings:
            st.info("No holdings found.")
        else:
            df = pd.DataFrame(holdings)

            # Select only relevant columns if available
            useful_cols = [
                "tradingsymbol", "quantity", "average_price", "last_price",
                "pnl", "instrument_token"
            ]
            df = df[[c for c in useful_cols if c in df.columns]]

            # Rename for clarity
            df.rename(columns={
                "tradingsymbol": "Symbol",
                "quantity": "Quantity",
                "average_price": "Avg Price (₹)",
                "last_price": "Last Price (₹)",
                "pnl": "Profit/Loss (₹)"
            }, inplace=True)

            # Add computed value
            if "Quantity" in df.columns and "Last Price (₹)" in df.columns:
                df["Current Value (₹)"] = df["Quantity"] * df["Last Price (₹)"]

            # Display metrics
            st.metric("Total Holdings", len(df))
            st.metric("Total Value (₹)", f"{df['Current Value (₹)'].sum():,.2f}")
            st.metric("Net P&L (₹)", f"{df['Profit/Loss (₹)'].sum():,.2f}")

            # Styled dataframe
            st.dataframe(
                df.style.format({
                    "Avg Price (₹)": "₹{:.2f}",
                    "Last Price (₹)": "₹{:.2f}",
                    "Profit/Loss (₹)": "₹{:.2f}",
                    "Current Value (₹)": "₹{:.2f}"
                }).background_gradient(
                    subset=["Profit/Loss (₹)"], cmap="RdYlGn"
                ),
                use_container_width=True
            )


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

        # ✅ Ensure both are lists before combining
        if isinstance(holdings, dict):
            holdings = [holdings]
        if isinstance(positions, dict):
            positions = [positions]

        all_data = holdings + positions

        if not all_data:
            st.info("No portfolio data available.")
            return

        summary = []
        for item in all_data:
            symbol = item.get("tradingsymbol") or item.get("symbol")
            qty = item.get("quantity", 0)
            last_price = item.get("last_price", 0) or 0

            # ✅ Fallback to FMP price
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
