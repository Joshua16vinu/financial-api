import requests
import pandas as pd
import streamlit as st

FMP_API_KEY = st.secrets.get("fmp_api_key", "YOUR_FMP_KEY")  # store in secrets.toml
BASE_URL = "https://financialmodelingprep.com/api/v3"

# --- Historical Stock Data ---
def get_historical_data(symbol="RELIANCE", period="6mo"):
    """Fetch historical OHLC data for a symbol."""
    url = f"{BASE_URL}/historical-price-full/{symbol}?apikey={FMP_API_KEY}"
    res = requests.get(url).json()
    if "historical" in res:
        df = pd.DataFrame(res["historical"])
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").set_index("date")
        return df
    return pd.DataFrame()

# --- Company Info ---
def get_company_info(symbol="RELIANCE"):
    url = f"{BASE_URL}/profile/{symbol}?apikey={FMP_API_KEY}"
    res = requests.get(url).json()
    if res:
        info = res[0]
        return {
            "Name": info.get("companyName"),
            "Sector": info.get("sector"),
            "Industry": info.get("industry"),
            "Market Cap": info.get("mktCap"),
            "P/E Ratio": info.get("priceEarningsRatio"),
            "52 Week High": info.get("range52WeekHigh"),
            "52 Week Low": info.get("range52WeekLow"),
            "Beta": info.get("beta"),
            "Website": info.get("website"),
            "Employees": info.get("fullTimeEmployees"),
            "Description": info.get("description"),
            "Exchange": info.get("exchangeShortName"),
            "Logo": info.get("image")
        }
    return {}


# --- Latest Price Fallback ---
@st.cache_data(ttl=3600)
def get_latest_price(symbol: str):
    """
    Fetch latest stock price for an Indian stock using FMP.
    Falls back to .NS (NSE) if symbol is plain.
    """
    if not symbol:
        return 0.0

    # normalize: ensure we query FMP with .NS suffix
    query_symbol = symbol if "." in symbol else f"{symbol}.NS"
    url = f"{BASE_URL}/quote/{query_symbol}?apikey={FMP_API_KEY}"

    try:
        res = requests.get(url, timeout=5)
        data = res.json()
        if isinstance(data, list) and len(data) > 0:
            return round(float(data[0].get("price", 0)), 2)
    except Exception as e:
        st.warning(f"FMP price fetch failed for {symbol}: {e}")

    return 0.0
