import streamlit as st
from openai import OpenAI
from portfolio import get_portfolio_value

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["openai_api_key"])

# --- Session state for persistent context ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "context_memory" not in st.session_state:
    st.session_state.context_memory = ""


def add_to_context(new_context):
    """Merge new financial data (portfolio summary) into long-term context."""
    st.session_state.context_memory += f"\n{new_context}\n"


def ai_portfolio_insights():
    """Automatically fetch live portfolio, generate insights, and store in context."""
    portfolio_snapshot, total_value = get_portfolio_value()
    prompt = f"""
My portfolio contains the following holdings:

{portfolio_snapshot}

Total portfolio value: ₹{total_value:,.2f}

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


def ai_chat(user_query):
    """
    Chat interface for the financial assistant.
    Automatically includes current portfolio context.
    """
    # Include portfolio snapshot in extra context
    portfolio_snapshot, _ = get_portfolio_value()
    combined_context = st.session_state.context_memory + f"\nPortfolio Snapshot: {portfolio_snapshot}"

    system_prompt = f"""
You are a personalised financial assistant. Use the following context to answer the question:
{combined_context}
"""

    messages = [{"role": "system", "content": system_prompt}]
    # include last 5 chat messages
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
