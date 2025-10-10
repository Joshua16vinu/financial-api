# kite_api.py
from kiteconnect import KiteConnect
import yfinance as yf
import os

KITE_API_KEY = os.getenv("KITE_API_KEY")
KITE_ACCESS_TOKEN = os.getenv("KITE_ACCESS_TOKEN")

kite = None
if KITE_API_KEY and KITE_ACCESS_TOKEN:
    try:
        kite = KiteConnect(api_key=KITE_API_KEY)
        kite.set_access_token(KITE_ACCESS_TOKEN)
    except Exception as e:
        print("Kite setup error:", e)

def get_live_quote(symbol: str) -> float:
    """Fetch live stock price; fallback to yFinance if Kite fails."""
    try:
        if kite:
            quote = kite.ltp(f"NSE:{symbol}")
            return quote[f"NSE:{symbol}"]["last_price"]
        else:
            raise Exception("Kite not configured")
    except Exception as e:
        print("Falling back to yFinance:", e)
        try:
            data = yf.Ticker(symbol + ".NS").history(period="1d")
            return round(float(data["Close"].iloc[-1]), 2)
        except Exception as e2:
            print("Fallback failed:", e2)
            return 0.0
