from kiteconnect import KiteConnect
import streamlit as st

API_KEY = st.secrets["kite_api_key"]
API_SECRET = st.secrets["kite_api_secret"]

kite = KiteConnect(api_key=API_KEY)

# --- Login URL Helper ---
def get_login_url():
    return kite.login_url()

# --- Generate Access Token from Request Token ---
def generate_access_token(request_token):
    try:
        data = kite.generate_session(request_token, api_secret=API_SECRET)
        access_token = data["access_token"]
        kite.set_access_token(access_token)
        return access_token
    except Exception as e:
        return f"Error: {str(e)}"

# --- Live Quote ---
def get_live_quote(symbol="RELIANCE"):
    try:
        instruments = kite.ltp(f"NSE:{symbol}")
        return instruments[f"NSE:{symbol}"]["last_price"]
    except Exception as e:
        return f"Error fetching live quote: {str(e)}"
