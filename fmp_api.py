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
    """Fetch company fundamentals + key market stats (works for Indian stocks)."""
    query_symbol = symbol if "." in symbol else f"{symbol}.NS"

    profile_url = f"{BASE_URL}/profile/{query_symbol}?apikey={FMP_API_KEY}"
    quote_url = f"{BASE_URL}/quote/{query_symbol}?apikey={FMP_API_KEY}"

    profile_data, quote_data = {}, {}

    try:
        profile_res = requests.get(profile_url).json()
        if isinstance(profile_res, list) and len(profile_res) > 0:
            profile_data = profile_res[0]
    except Exception as e:
        st.warning(f"Profile fetch failed: {e}")

    try:
        quote_res = requests.get(quote_url).json()
        if isinstance(quote_res, list) and len(quote_res) > 0:
            quote_data = quote_res[0]
    except Exception as e:
        st.warning(f"Quote fetch failed: {e}")

    return {
        "Name": profile_data.get("companyName") or query_symbol,
        "Sector": profile_data.get("sector"),
        "Industry": profile_data.get("industry"),
        "Market Cap": quote_data.get("marketCap"),
        "P/E Ratio": quote_data.get("pe"),
        "52 Week High": quote_data.get("yearHigh"),
        "52 Week Low": quote_data.get("yearLow"),
        "Beta": quote_data.get("beta"),
        "Volume": quote_data.get("volume"),
        "Exchange": quote_data.get("exchangeShortName"),
        "Description": profile_data.get("description"),
        "Website": profile_data.get("website"),
    }



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
