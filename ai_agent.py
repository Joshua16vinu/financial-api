# ai_agent.py
import streamlit as st
from openai import OpenAI

# Initialize OpenAI client using Streamlit secrets
client = OpenAI(api_key=st.secrets["openai_api_key"])

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
    context: optional string containing portfolio or market info
    """
    prompt = f"{context}\nUser: {user_query}\nAssistant:"
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return response.choices[0].message.content
