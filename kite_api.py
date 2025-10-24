import streamlit as st
from kiteconnect import KiteConnect
import pandas as pd

# -------------------------------------
# 🔐 Initialize Kite client safely
# -------------------------------------
def get_kite_client():
    try:
        api_key = st.secrets["kite_api_key"]
        kite = KiteConnect(api_key=api_key)
        access_token = st.session_state.get("access_token")

        if access_token:
            kite.set_access_token(access_token)
        else:
            st.warning("⚠️ No access token found. Please authenticate via sidebar.")
        return kite
    except Exception as e:
        st.error(f"Error initializing Kite client: {e}")
        return None


# -------------------------------------
# 🔑 Authentication
# -------------------------------------
def get_login_url():
    kite = KiteConnect(api_key=st.secrets["kite_api_key"])
    return kite.login_url()


def generate_access_token(request_token):
    try:
        kite = KiteConnect(api_key=st.secrets["kite_api_key"])
        data = kite.generate_session(request_token, api_secret=st.secrets["kite_api_secret"])
        return data["access_token"]
    except Exception as e:
        return f"Error generating token: {e}"


# -------------------------------------
# 📊 Core Account Info
# -------------------------------------
def get_positions():
    kite = get_kite_client()
    if not kite:
        return []
    try:
        data = kite.positions()
        return data.get("net", [])
    except Exception as e:
        st.error(f"Error fetching positions: {e}")
        return []


def get_holdings():
    kite = get_kite_client()
    if not kite:
        return []
    try:
        return kite.holdings()
    except Exception as e:
        st.error(f"Error fetching holdings: {e}")
        return []


def get_funds():
    kite = get_kite_client()
    if not kite:
        return {}
    try:
        return kite.margins()
    except Exception as e:
        st.error(f"Error fetching funds: {e}")
        return {}


# -------------------------------------
# 💸 Trading & Orders
# -------------------------------------
def place_order(symbol, qty, order_type, trans_type, price=0.0):
    kite = get_kite_client()
    if not kite:
        return "Client not initialized"

    try:
        order_id = kite.place_order(
            tradingsymbol=symbol,
            exchange="NSE",
            transaction_type=trans_type,
            quantity=qty,
            order_type=order_type,
            product="CNC",
            price=price if order_type == "LIMIT" else None,
        )
        return f"✅ Order placed successfully! Order ID: {order_id}"
    except Exception as e:
        return f"Error placing order: {e}"


# -------------------------------------
# 🎯 GTT Orders & Alerts
# -------------------------------------
def create_gtt(symbol, trigger_price, qty):
    kite = get_kite_client()
    if not kite:
        return "Client not initialized"
    try:
        return kite.place_gtt(
            trigger_type="single",
            tradingsymbol=symbol,
            exchange="NSE",
            trigger_values=[trigger_price],
            last_price=trigger_price,
            orders=[{
                "transaction_type": "BUY",
                "quantity": qty,
                "price": trigger_price
            }]
        )
    except Exception as e:
        return f"Error creating GTT: {e}"


def list_gtt_orders():
    kite = get_kite_client()
    if not kite:
        return []
    try:
        return kite.gtts()
    except Exception as e:
        st.error(f"Error fetching GTT orders: {e}")
        return []


def create_alert(symbol, alert_price, note):
    return f"Alert set for {symbol} at ₹{alert_price} ({note})"


def get_alerts():
    return [{"symbol": "RELIANCE", "alert_price": 2500, "note": "Test alert"}]


# -------------------------------------
# 💰 Margin Requirements
# -------------------------------------
def get_margin_requirements(symbol, qty):
    try:
        order_data = [{
            "exchange": "NSE",
            "tradingsymbol": symbol,
            "transaction_type": "BUY",
            "variety": "regular",
            "product": "CNC",
            "order_type": "MARKET",
            "quantity": int(qty),
            "price": 0
        }]
        # Try modern format first
        return kite.order_margins(order_data)
    except TypeError:
        # fallback to old style for legacy users
        try:
            return kite.order_margins(
                exchange="NSE",
                tradingsymbol=symbol,
                transaction_type="BUY",
                variety="regular",
                product="CNC",
                order_type="MARKET",
                quantity=int(qty),
                price=0
            )
        except Exception as e:
            return {"error": f"Error checking margin: {e}"}


# -------------------------------------
# 📈 Live Quotes
# -------------------------------------
def get_live_quote(symbol):
    kite = get_kite_client()
    if not kite:
        return 0.0
    try:
        quote = kite.ltp(f"NSE:{symbol}")
        return quote[f"NSE:{symbol}"]["last_price"]
    except Exception as e:
        st.error(f"Error fetching quote for {symbol}: {e}")
        return 0.0
