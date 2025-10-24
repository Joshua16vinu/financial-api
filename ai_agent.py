import streamlit as st
import google.generativeai as genai
from kite_api import get_holdings, get_positions
from fmp_api import get_latest_price

# -----------------------------
# 🔑 Initialize Gemini client
# -----------------------------
genai.configure(api_key=st.secrets.get("gemini_api_key"))
model = genai.GenerativeModel("gemini-2.5-flash")

# --- Safe Session Initialization ---
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "context_memory" not in st.session_state:
    st.session_state["context_memory"] = ""


# -----------------------------
# 🧩 Helper: Context Management
# -----------------------------
def add_to_context(new_context: str):
    """Safely append context data to Streamlit session."""
    current_context = st.session_state.get("context_memory", "")
    st.session_state["context_memory"] = current_context + f"\n{new_context}\n"


# -----------------------------
# 📊 Portfolio Snapshot
# -----------------------------
def get_portfolio_snapshot():
    """Fetch current holdings & positions with FMP fallback."""
    snapshot = []
    holdings = get_holdings() or []
    positions = get_positions() or []

    if not isinstance(holdings, list):
        holdings = [holdings]
    if not isinstance(positions, list):
        positions = [positions]

    all_data = holdings + positions
    for item in all_data:
        symbol = item.get("symbol") or item.get("tradingsymbol")
        qty = item.get("quantity", 0)
        last_price = item.get("last_price", 0) or 0

        # ✅ fallback to FMP if Kite price missing
        if not last_price or last_price == 0:
            last_price = get_latest_price(symbol)

        snapshot.append({
            "symbol": symbol,
            "quantity": qty,
            "last_price": round(last_price, 2),
            "value": round(qty * last_price, 2),
        })

    return snapshot


# -----------------------------
# 🧠 Portfolio Insights via AI (Gemini)
# -----------------------------
def ai_portfolio_insights():
    """Generate AI-based portfolio insights using Gemini."""
    portfolio_data = get_portfolio_snapshot()
    add_to_context(str(portfolio_data))

    prompt = f"""
You are a financial analyst AI assisting an investor in reviewing their equity portfolio.

Your task is to perform a deep portfolio analysis based on the data provided below.

Portfolio Data:
{portfolio_data}

Analyze and provide a structured report covering the following points:

1. **Portfolio Overview**
   - Summarize total holdings, invested capital, and current valuation.
   - Highlight portfolio trend (bullish/bearish/neutral).

2. **Top Performers**
   - Identify the top 3–5 performing stocks.
   - Mention whether to continue holding or book partial profits with their reasons (if inferable).

3. **Underperformers**
   - List the lowest 3–5 performing holdings.
   - Provide reasons for underperformance (e.g., sector slump, high volatility, weak fundamentals) if possible.
   - Recommend actions: hold, average down, or exit.

4. **Risk and Diversification Assessment**
   - Evaluate portfolio concentration (e.g., too many small/mid-caps, single sector exposure, etc.).
   - Mention liquidity risk or volatility risk if identifiable.
   - Suggest diversification or hedging ideas (like ETFs, blue-chips, or sector rotation).

5. **Rebalancing Recommendations**
   - Suggest what to buy, sell, or rebalance.
   - Indicate target allocation changes (e.g., “Reduce exposure to small-caps from 40% → 25%”).
   - Include short-term vs long-term perspective.

6. **Actionable Summary**
   - Bullet-point key takeaways for the user.
   - Keep the summary concise, focusing on what actions to take this week or month.
   - Keep it within 2 sentences

7. **Tone and Output Format**
   - Use a clear, investor-friendly tone.
   - Structure the output with headings, bullet points, and short paragraphs.
   - Provide insights as if writing a mini portfolio report (not just a list).

Return only the analysis in markdown format.
"""


    try:
        response = model.generate_content(prompt)
        insights = response.text
    except Exception as e:
        insights = f"Error fetching insights: {e}"

    add_to_context(f"Portfolio Insights: {insights}")
    return insights


# -----------------------------
# 💬 AI Chat Interface (Gemini)
# -----------------------------
def ai_chat(user_query: str):
    """Chat interface for financial assistant."""
    context_memory = st.session_state.get("context_memory", "")
    chat_history = st.session_state.get("chat_history", [])

    system_prompt = f"""
You are a helpful financial assistant. Use the following context when responding:
{context_memory}
"""

    # Combine system prompt + last few messages
    history_text = "\n".join(
        [f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_history[-5:]]
    )
    full_prompt = f"{system_prompt}\n\n{history_text}\n\nUser: {user_query}\nAssistant:"

    try:
        response = model.generate_content(full_prompt)
        answer = response.text
    except Exception as e:
        answer = f"Error: {e}"

    # update session state safely
    chat_history.append({"role": "user", "content": user_query})
    chat_history.append({"role": "assistant", "content": answer})
    st.session_state["chat_history"] = chat_history

    return answer
