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
    # Initialize context memory if it doesn't exist
    if "context_memory" not in st.session_state:
        st.session_state.context_memory = ""

    # Append current portfolio/context to memory
    st.session_state.context_memory += f"\n{context}"

    # Build prompt including previous memory
    prompt = f"{st.session_state.context_memory}\nUser: {user_query}\nAssistant:"

    # Generate response
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )

    return response.choices[0].message.content
