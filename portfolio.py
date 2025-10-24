import pandas as pd
import streamlit as st
from kite_api import get_holdings
from fmp_api import get_historical_data

# -----------------------------
# 🧠 Portfolio Value Calculation
# -----------------------------
def get_portfolio_value():
    """
    Fetch holdings from Kite API and calculate total portfolio value
    using live prices from FMP API.
    """
    try:
        holdings = get_holdings()
    except Exception as e:
        st.error(f"Error fetching holdings: {e}")
        return 0, pd.DataFrame()

    # Ensure holdings is a list of dicts
    if not isinstance(holdings, list):
        holdings = [holdings]

    # Convert to DataFrame safely
    if len(holdings) == 0:
        st.warning("No holdings found.")
        return 0, pd.DataFrame()

    holdings_df = pd.DataFrame(holdings)

    total_value = 0
    portfolio_data = []

    # -----------------------------
    # 🔁 Loop through each holding
    # -----------------------------
    for _, row in holdings_df.iterrows():
        symbol = row.get("symbol") or row.get("tradingsymbol")
        qty = row.get("quantity", 0)

        if not symbol:
            continue

        # Fetch latest close price from FMP API
        try:
            price_df = get_historical_data(symbol)
            if not price_df.empty:
                last_price = price_df["close"].iloc[-1]
            else:
                last_price = 0.0
        except Exception as e:
            st.warning(f"Error fetching price for {symbol}: {e}")
            last_price = 0.0

        # Calculate position value
        value = qty * last_price
        total_value += value

        portfolio_data.append({
            "Symbol": symbol,
            "Quantity": qty,
            "Last Price": round(last_price, 2),
            "Value (₹)": round(value, 2),
        })

    # Convert computed portfolio into DataFrame
    portfolio_df = pd.DataFrame(portfolio_data)

    return total_value, portfolio_df


# -----------------------------
# 📊 Portfolio Summary Section
# -----------------------------
def show_portfolio_summary():
    """
    Display portfolio value and table in Streamlit.
    """
    st.subheader("📈 Portfolio Summary")

    total_value, portfolio_df = get_portfolio_value()

    if portfolio_df.empty:
        st.info("No portfolio data to display.")
        return

    st.metric("Total Portfolio Value (₹)", f"{total_value:,.2f}")

    st.dataframe(
        portfolio_df.style.format({
            "Last Price": "₹{:.2f}",
            "Value (₹)": "₹{:.2f}"
        }),
        use_container_width=True
    )


# -----------------------------
# 🧾 Run Section (if standalone)
# -----------------------------
if __name__ == "__main__":
    st.title("💹 Portfolio Analyzer")
    show_portfolio_summary()
