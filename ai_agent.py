import streamlit as st
from openai import OpenAI
from kite_api import get_holdings, get_positions
from fmp_api import get_historical_data

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets.get("openai_api_key"))

# -----------------------------
# Session State for Chat & Memory
# -----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "context_memory" not in st.session_state:
    st.session_state.context_memory = ""


def add_to_context(new_context):
    """Merge new financial data into long-term context."""
    st.session_state.context_memory += f"\n{new_context}\n"


def get_portfolio_snapshot():
    """Fetch current holdings & positions with live FMP prices."""
    snapshot = []
    for item in get_holdings() + get_positions():
        symbol = item.get("symbol") or item.get("tradingsymbol")
        qty = item.get("quantity", 0)
        try:
            price_df = get_historical_data(symbol)
            last_price = price_df["close"].iloc[-1] if not price_df.empty else 0.0
        except:
            last_price = 0.0
        snapshot.append({
            "symbol": symbol,
            "quantity": qty,
            "last_price": round(last_price, 2),
            "value": round(qty * last_price, 2),
        })
    return snapshot


def ai_portfolio_insights():
    """Generate AI insights for current portfolio."""
    portfolio_data = get_portfolio_snapshot()
    add_to_context(str(portfolio_data))

    prompt = f"""
Analyze the following portfolio and provide:

1. Top performers
2. Underperformers
3. Rebalancing suggestions
4. Risk assessment
5. Actionable summary

Portfolio: {portfolio_data}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )

    insights = response.choices[0].message.content
    add_to_context(f"Portfolio Insights: {insights}")
    return insights


def ai_chat(user_query):
    """
    Chat interface for financial assistant.
    Uses portfolio context stored in session state.
    """
    combined_context = st.session_state.context_memory
    system_prompt = f"""
You are a personalized financial assistant. Use this context to answer questions:

{combined_context}
"""
    messages = [{"role": "system", "content": system_prompt}]
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
