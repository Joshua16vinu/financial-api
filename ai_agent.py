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
    """Fetch current holdings & positions safely with live FMP prices."""
    try:
        holdings = get_holdings() or []
        positions = get_positions() or []
    except Exception as e:
        st.error(f"Error fetching portfolio data: {e}")
        return []

    # Normalize structures
    if not isinstance(holdings, list):
        holdings = [holdings]
    if not isinstance(positions, list):
        positions = [positions]

    snapshot = []
    for item in holdings + positions:
        symbol = item.get("symbol") or item.get("tradingsymbol")
        qty = item.get("quantity", 0)
        if not symbol:
            continue
        try:
            price_df = get_historical_data(symbol)
            last_price = price_df["close"].iloc[-1] if not price_df.empty else 0.0
        except Exception as e:
            st.warning(f"Error fetching price for {symbol}: {e}")
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
    if not portfolio_data:
        return "⚠️ No portfolio data found. Please ensure Kite is connected."

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

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        insights = response.choices[0].message.content
        add_to_context(f"Portfolio Insights: {insights}")
        return insights
    except Exception as e:
        st.error(f"AI error: {e}")
        return "⚠️ Could not generate AI insights. Please check your API key or try again later."


def ai_chat(user_query):
    """Conversational AI chat with contextual memory."""
    combined_context = st.session_state.context_memory
    system_prompt = f"""
You are a personalized financial assistant.
Use this context to answer questions about portfolio holdings, positions, and strategies.

Context:
{combined_context}
"""
    messages = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.chat_history[-5:]:
        messages.append(msg)
    messages.append({"role": "user", "content": user_query})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.5,
        )
        answer = response.choices[0].message.content
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        return answer
    except Exception as e:
        st.error(f"Chat error: {e}")
        return "⚠️ Unable to fetch AI response at this time."
