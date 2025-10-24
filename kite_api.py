import streamlit as st
from kiteconnect import KiteConnect
import requests

# --- Load from secrets ---
API_KEY = st.secrets.get("kite_api_key")
API_SECRET = st.secrets.get("kite_api_secret")

# --- Global Kite instance (initialized later) ---
kite = None


# -----------------------------
# 🔑 AUTHENTICATION
# -----------------------------
def get_login_url():
    """Generate login URL for Kite authentication."""
    global kite
    kite = KiteConnect(api_key=API_KEY)
    return kite.login_url()


def generate_access_token(request_token: str):
    """Exchange request token for access token."""
    global kite
    try:
        if kite is None:
            kite = KiteConnect(api_key=API_KEY)
        data = kite.generate_session(request_token, api_secret=API_SECRET)
        access_token = data["access_token"]
        kite.set_access_token(access_token)
        st.session_state["access_token"] = access_token
        return access_token
    except Exception as e:
        return f"Error generating access token: {e}"


# -----------------------------
# 💹 LIVE QUOTES & MARKET DATA
# -----------------------------
def get_live_quote(symbol):
    """Fetch live price for a symbol."""
    try:
        if kite is None:
            return "Not authenticated"
        quote = kite.ltp(f"NSE:{symbol}")
        return quote[f"NSE:{symbol}"]["last_price"]
    except Exception as e:
        return f"Error fetching quote: {e}"


# -----------------------------
# 📊 PORTFOLIO DATA
# -----------------------------
def get_holdings():
    """Fetch user holdings."""
    try:
        if kite is None:
            return []
        return kite.holdings()
    except Exception as e:
        return {"error": str(e)}


def get_positions():
    """Fetch user positions."""
    try:
        if kite is None:
            return []
        return kite.positions()["net"]
    except Exception as e:
        return {"error": str(e)}


def get_funds():
    """Fetch available funds/margins."""
    try:
        if kite is None:
            return {}
        return kite.margins()
    except Exception as e:
        return {"error": str(e)}


# -----------------------------
# 🧾 ORDER PLACEMENT
# -----------------------------
def place_order(symbol, qty, order_type, trans_type, price=0):
    """Place a buy/sell order."""
    try:
        if kite is None:
            return {"error": "Not authenticated"}
        order_id = kite.place_order(
            variety="regular",
            exchange="NSE",
            tradingsymbol=symbol,
            transaction_type=trans_type,
            quantity=int(qty),
            order_type=order_type,
            product="CNC",
            price=float(price),
        )
        return {"success": True, "order_id": order_id}
    except Exception as e:
        return {"error": str(e)}


# -----------------------------
# ⏰ GTT ORDERS
# -----------------------------
def create_gtt(symbol, trigger_price, qty):
    try:
        if kite is None:
            return {"error": "Not authenticated"}
        gtt = kite.place_gtt(
            trigger_type="single",
            tradingsymbol=symbol,
            exchange="NSE",
            trigger_values=[float(trigger_price)],
            last_price=trigger_price,
            orders=[{
                "transaction_type": "BUY",
                "quantity": int(qty),
                "price": float(trigger_price)
            }],
        )
        return {"success": True, "gtt_id": gtt}
    except Exception as e:
        return {"error": str(e)}


def list_gtt_orders():
    try:
        if kite is None:
            return []
        return kite.get_gtts()
    except Exception as e:
        return {"error": str(e)}


# -----------------------------
# ⚡ ALERTS & MARGINS
# -----------------------------
def create_alert(symbol, price, note):
    """Create a mock alert (not real Kite alert)."""
    return {"symbol": symbol, "price": price, "note": note}


def get_alerts():
    """List alerts from session."""
    return st.session_state.get("alerts", [])


def get_margin_requirements(symbol, qty):
    """Check margin requirement using latest Kite API format."""
    global kite
    try:
        if kite is None:
            return {"error": "Not authenticated"}

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
        margin = kite.order_margins(order_data)
        return margin
    except Exception as e:
        return {"error": f"Error checking margin: {e}"}
