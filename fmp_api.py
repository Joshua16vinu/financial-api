import requests
import pandas as pd
import streamlit as st

FMP_API_KEY = st.secrets.get("fmp_api_key", "YOUR_FMP_KEY")  # store in secrets.toml

BASE_URL = "https://financialmodelingprep.com/api/v3"

# --- Historical Stock Data ---
def get_historical_data(symbol="RELIANCE", period="6mo"):
    url = f"{BASE_URL}/historical-price-full/{symbol}?apikey={FMP_API_KEY}"
    res = requests.get(url).json()
    if "historical" in res:
        df = pd.DataFrame(res["historical"])
        df["date"] = pd.to_datetime(df["date"])
        # Keep last ~6 months
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
            "Market Cap": info.get("mktCap"),
            "P/E Ratio": info.get("priceEarningsRatio"),
            "52 Week High": info.get("range52WeekHigh"),
            "52 Week Low": info.get("range52WeekLow"),
        }
    return {}
