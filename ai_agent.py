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


def ai_portfolio_insights(portfolio_summary):
    """Generate AI insights for the portfolio and store them in context."""
    prompt = f"""
    My portfolio contains: {portfolio_summary}.
    Provide:
    1. Top gainers
    2. Top losers
    3. Rebalancing suggestions
    Present concisely for dashboard display.
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
    You are a financial assistant. Use the following context to answer the question:
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
