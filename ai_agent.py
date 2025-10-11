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


def ai_chat(user_query):
    """
    Chat interface for the financial assistant.
    - Uses previous chat history and context_memory
    - Adds each user+assistant exchange back into memory
    """
    # Combine all relevant context (portfolio, mutual funds, history)
    system_prompt = f"""
    You are a financial assistant. Use the following context to answer the question.
    Context:
    {st.session_state.context_memory}
    """

    messages = [{"role": "system", "content": system_prompt}]

    # Include previous chat history for continuity
    for msg in st.session_state.chat_history[-5:]:  # limit to last 5 exchanges
        messages.append(msg)

    messages.append({"role": "user", "content": user_query})

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.5,
    )

    answer = response.choices[0].message.content

    # Save chat exchange in session state
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    st.session_state.chat_history.append({"role": "assistant", "content": answer})

    return answer
