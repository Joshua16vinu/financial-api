import streamlit as st
import yfinance as yf
from kiteconnect import KiteConnect

API_KEY = st.secrets.get("kite_api_key")
API_SECRET = st.secrets.get("kite_api_secret")

kite = None
if API_KEY:
    try:
        kite = KiteConnect(api_key=API_KEY)
    except Exception as e:
        st.warning(f"Kite initialization error: {e}")

# --- Login URL Helper ---
def get_login_url():
    if kite:
        return kite.login_url()
    return None

# --- Generate Access Token from Request Token ---
def generate_access_token(request_token):
    if not kite:
        return "Error: Kite not initialized"
    try:
        data = kite.generate_session(request_token, api_secret=API_SECRET)
        access_token = data["access_token"]
        kite.set_access_token(access_token)
        return access_token
    except Exception as e:
        return f"Error: {str(e)}"

# --- Live Quote with yFinance fallback ---
def get_live_quote(symbol="RELIANCE"):
    """Fetch live stock price; show Kite error to user and fallback to yFinance"""
    # Try Kite first
    if kite:
        try:
            instruments = kite.ltp(f"NSE:{symbol}")
            return instruments[f"NSE:{symbol}"]["last_price"]
        except Exception as e:
            st.error(f"Kite fetch failed for {symbol}: {e}")
    
    # Fallback to yFinance
    try:
        data = yf.Ticker(symbol + ".NS").history(period="1d")
        price = round(float(data["Close"].iloc[-1]), 2)
        st.info(f"Using yFinance fallback for {symbol}")
        return price
    except Exception as e2:
        st.error(f"yFinance fallback failed for {symbol}: {e2}")
        return 0.0
