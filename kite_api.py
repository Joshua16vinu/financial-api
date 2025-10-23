import streamlit as st
import pandas as pd
from kiteconnect import KiteConnect
import yfinance as yf

# --- KITE INITIALIZATION ---
KITE_API_KEY = st.secrets["kite"]["api_key"]
KITE_API_SECRET = st.secrets["kite"]["api_secret"]

kite = KiteConnect(api_key=KITE_API_KEY)


# --- STEP 1: Generate Kite Login URL ---
def get_login_url():
    """Generate the login URL for the user to authorize the app."""
    try:
        return kite.login_url()
    except Exception as e:
        return f"Error: {str(e)}"


# --- STEP 2: Exchange Request Token for Access Token ---
def generate_access_token(request_token: str):
    """Exchange request token for access token (valid for one session/day)."""
    try:
        session_data = kite.generate_session(request_token, api_secret=KITE_API_SECRET)
        access_token = session_data["access_token"]
        kite.set_access_token(access_token)
        st.session_state["access_token"] = access_token
        return access_token
    except Exception as e:
        return f"Error: {str(e)}"


# --- STEP 3: Fetch Live Quote (with fallback to yFinance) ---
def get_live_quote(symbol: str):
    """Fetch live stock price using Kite; fallback to yFinance if needed."""
    if "access_token" not in st.session_state:
        st.warning("Please generate Kite access token first.")
        return 0.0

    try:
        data = kite.ltp(f"NSE:{symbol}")
        return data[f"NSE:{symbol}"]["last_price"]
    except Exception as e:
        st.error(f"Kite API failed for {symbol}: {e}")
        # fallback
        try:
            df = yf.Ticker(symbol + ".NS").history(period="1d")
            price = round(float(df["Close"].iloc[-1]), 2)
            st.info(f"Using yFinance fallback for {symbol}")
            return price
        except Exception as e2:
            st.error(f"yFinance fallback failed: {e2}")
            return 0.0


# --- STEP 4: Fetch User Positions (Kite Only) ---
def get_positions():
    """Fetch user's current holdings/positions from Kite."""
    if "access_token" not in st.session_state:
        return pd.DataFrame({"Error": ["Access token not generated yet."]})

    try:
        positions = kite.positions()["net"]
        if not positions:
            return pd.DataFrame({"Message": ["No active positions found."]})
        df = pd.DataFrame(positions)
        return df[["tradingsymbol", "quantity", "average_price", "last_price", "pnl"]]
    except Exception as e:
        return pd.DataFrame({"Error": [str(e)]})
