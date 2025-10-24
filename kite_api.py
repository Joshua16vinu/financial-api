# kite_api.py

import streamlit as st
import yfinance as yf
from kiteconnect import KiteConnect, KiteTicker

API_KEY = st.secrets.get("kite_api_key")
API_SECRET = st.secrets.get("kite_api_secret")

kite = None
if API_KEY:
    try:
        kite = KiteConnect(api_key=API_KEY)
    except Exception as e:
        st.warning(f"Kite initialization error: {e}")

# --- LOGIN URL ---
def get_login_url():
    if kite:
        return kite.login_url()
    return None

# --- GENERATE ACCESS TOKEN ---
def generate_access_token(request_token):
    if not kite:
        return "Error: Kite not initialized"
    try:
        data = kite.generate_session(request_token, api_secret=API_SECRET)
        access_token = data["access_token"]
        kite.set_access_token(access_token)
        st.session_state["kite"] = kite
        return access_token
    except Exception as e:
        return f"Error: {str(e)}"

# --- GET LIVE QUOTE ---
def get_live_quote(symbol="RELIANCE"):
    if kite:
        try:
            instruments = kite.ltp(f"NSE:{symbol}")
            return instruments[f"NSE:{symbol}"]["last_price"]
        except Exception as e:
            st.error(f"Kite fetch failed for {symbol}: {e}")

    # fallback
    try:
        data = yf.Ticker(symbol + ".NS").history(period="1d")
        price = round(float(data["Close"].iloc[-1]), 2)
        st.info(f"Using yFinance fallback for {symbol}")
        return price
    except Exception as e2:
        st.error(f"yFinance fallback failed for {symbol}: {e2}")
        return 0.0


# --- PLACE ORDER ---
def place_order(symbol, qty, order_type="MARKET", transaction_type="BUY", price=None):
    """Place a market/limit/cover order"""
    if not kite:
        return {"error": "Kite not initialized"}
    try:
        order_id = kite.place_order(
            tradingsymbol=symbol,
            exchange="NSE",
            transaction_type=transaction_type,
            quantity=int(qty),
            order_type=order_type,
            price=price if price else 0,
            product="CNC",  # delivery for stocks
            variety="regular"
        )
        return {"success": True, "order_id": order_id}
    except Exception as e:
        return {"error": str(e)}


# --- POSITIONS / HOLDINGS / FUNDS ---
def get_positions():
    try:
        return kite.positions()
    except Exception as e:
        return {"error": str(e)}

def get_holdings():
    try:
        return kite.holdings()
    except Exception as e:
        return {"error": str(e)}

def get_funds():
    try:
        return kite.margins()
    except Exception as e:
        return {"error": str(e)}


# --- GTT ORDERS ---
def create_gtt(symbol, trigger_price, qty, order_type="BUY"):
    """Create a Good Till Triggered (GTT) order"""
    try:
        trigger = [{
            "exchange": "NSE",
            "tradingsymbol": symbol,
            "trigger_values": [trigger_price],
            "last_price": trigger_price,
            "orders": [{
                "transaction_type": order_type,
                "quantity": qty,
                "price": trigger_price
            }]
        }]
        return kite.place_gtt("single", trigger[0]["tradingsymbol"], trigger[0]["trigger_values"], trigger[0]["orders"])
    except Exception as e:
        return {"error": str(e)}

def list_gtt_orders():
    try:
        return kite.get_gtts()
    except Exception as e:
        return {"error": str(e)}

def delete_gtt(order_id):
    try:
        kite.delete_gtt(order_id)
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}


# --- ALERT MANAGEMENT ---
def create_alert(symbol, price, note="Price Alert"):
    """Store user-defined alerts locally in Streamlit session"""
    if "alerts" not in st.session_state:
        st.session_state["alerts"] = []
    st.session_state["alerts"].append({"symbol": symbol, "price": price, "note": note})
    return {"success": True, "message": f"Alert for {symbol} at ₹{price} added."}

def get_alerts():
    return st.session_state.get("alerts", [])

# --- MARGIN COMPUTATION ---
def get_margin_requirements(symbol="RELIANCE", qty=1, transaction_type="BUY"):
    """Fetch margin requirements for given order"""
    try:
        margin = kite.order_margins([
            {
                "exchange": "NSE",
                "tradingsymbol": symbol,
                "transaction_type": transaction_type,
                "variety": "regular",
                "product": "CNC",
                "order_type": "MARKET",
                "quantity": qty
            }
        ])
        return margin[0]
    except Exception as e:
        return {"error": str(e)}


# --- PORTFOLIO SUMMARY ---
def get_portfolio_summary():
    """Combine holdings + funds into unified summary"""
    holdings = get_holdings()
    funds = get_funds()
    if "error" in holdings:
        return {"error": holdings["error"]}
    portfolio_value = sum(float(h["last_price"]) * h["quantity"] for h in holdings)
    cash = funds.get("equity", {}).get("available", 0)
    return {
        "Holdings Count": len(holdings),
        "Portfolio Value": portfolio_value,
        "Available Funds": cash,
        "Total Equity Value": portfolio_value + cash,
    }
