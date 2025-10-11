import streamlit as st
from openai import OpenAI
import yfinance as yf
import pandas as pd

# Initialize client
client = OpenAI(api_key=st.secrets["openai_api_key"])

# --- Initialize Session State for Persistent Context ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "context_memory" not in st.session_state:
    st.session_state.context_memory = ""


def add_to_context(new_context):
    """Merge new financial data (like portfolio summary) into long-term context."""
    st.session_state.context_memory += f"\n{new_context}\n"


def fetch_live_portfolio_data(portfolio):
    """
    portfolio: list of dicts OR pandas DataFrame
    Returns portfolio with live price, % change, market value.
    """
    live_data = []

    # Convert DataFrame to list of dicts if needed
    if isinstance(portfolio, pd.DataFrame):
        portfolio = portfolio.to_dict(orient="records")

    for stock in portfolio:
        symbol = stock.get("symbol")
        qty = stock.get("quantity", 0)
        if not symbol:
            continue  # skip invalid entries
        try:
            ticker = yf.Ticker(symbol + ".NS")
            info = ticker.history(period="2d")  # get last 2 days for % change
            if len(info) < 1:
                raise ValueError("No data found")
            last_price = float(info["Close"].iloc[-1])
            prev_close = float(info["Close"].iloc[-2]) if len(info) > 1 else last_price
            change_pct = round((last_price - prev_close) / prev_close * 100, 2) if prev_close else 0
            market_value = last_price * qty
            live_data.append({
                "symbol": symbol,
                "quantity": qty,
                "last_price": last_price,
                "change_pct": change_pct,
                "market_value": market_value
            })
        except Exception as e:
            live_data.append({
                "symbol": symbol,
                "quantity": qty,
                "last_price": None,
                "change_pct": None,
                "market_value": None,
                "error": str(e)
            })
    return live_data



def ai_portfolio_insights(portfolio):
    """Generate AI insights for the portfolio and store them in context."""
    live_portfolio = fetch_live_portfolio_data(portfolio)
    df_portfolio = pd.DataFrame(live_portfolio)
    
    prompt = f"""
My portfolio contains the following holdings with live data: 
{df_portfolio.to_dict(orient='records')}

Please provide:

1. Top Performers (Gainers) - show symbol, % gain, reason.
2. Underperformers (Losers) - show symbol, % loss, reason.
3. Rebalancing Suggestions - which stocks to buy more, sell, or hold.
4. Risk Assessment - low/moderate/high, and why.
5. Actionable Summary - concise points suitable for dashboard cards.
"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )

    insights = response.choices[0].message.content
    add_to_context(f"Portfolio Summary and Insights: {insights}")
    return insights


def ai_chat(user_query, extra_context=""):
    """
    Chat interface for the financial assistant.
    Optionally accepts extra context (e.g., current portfolio snapshot)
    """
    combined_context = st.session_state.context_memory + f"\n{extra_context}"
    system_prompt = f"""
You are a personalized financial assistant. Use the following context to answer the user's question:
{combined_context}
"""
    messages = [{"role": "system", "content": system_prompt}]
    # include last 5 messages for context
    for msg in st.session_state.chat_history[-5:]:
        messages.append(msg)
    messages.append({"role": "user", "content": user_query})

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.5,
    )

    answer = response.choices[0].message.content
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    st.session_state.chat_history.append({"role": "assistant", "content": answer})
    return answer
