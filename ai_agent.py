import streamlit as st
from openai import OpenAI

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


def ai_portfolio_insights(portfolio_data):
    """Generate AI insights for the portfolio and store them in context."""
    prompt = f"""
My portfolio contains the following holdings: {portfolio_data}.
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
    Optionally accepts extra context (e.g. current portfolio snapshot)
    """
    combined_context = st.session_state.context_memory + f"\n{extra_context}"
    system_prompt = f"""
    You are a personalised financial assistant . Use the following context to answer the question:
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
