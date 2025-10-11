# ai_agent.py
import streamlit as st
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["openai_api_key"])

# --- Initialize session memory ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "context_memory" not in st.session_state:
    st.session_state.context_memory = ""


def ai_portfolio_insights(portfolio_summary):
    """
    Generate AI insights for the portfolio:
    - Top gainers / losers
    - Rebalancing suggestions
    """
    prompt = f"""
    My portfolio contains: {portfolio_summary}
    Please provide:
    1. Top gainers
    2. Top losers
    3. Suggestions for rebalancing
    Present the answer in simple, human-readable terms.
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return response.choices[0].message.content


def ai_chat(user_query, context=""):
    """
    Chat interface for the financial assistant.
    Keeps memory + allows optional dynamic context.
    """
    # Append new contextual info (like portfolio or MF summary)
    if context:
        st.session_state.context_memory += f"\n{context}"

    # Prepare system + conversation messages
    system_prompt = f"""
    You are a financial assistant and you must help user analyse the portfolio. Use the following context for reasoning:
    {st.session_state.context_memory}
    """

    messages = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.chat_history[-5:]:
        messages.append(msg)
    messages.append({"role": "user", "content": user_query})

    # Generate response
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.5,
    )
    answer = response.choices[0].message.content

    # Save to memory
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    st.session_state.chat_history.append({"role": "assistant", "content": answer})

    return answer
