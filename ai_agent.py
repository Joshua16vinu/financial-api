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
My portfolio currently contains the following holdings: {portfolio_summary}.

Please provide a detailed yet concise analysis including:

1. **Top Performers (Gainers)**:
   - List the assets/stocks/mutual funds that have shown the highest positive performance over the past period.
   - Include percentage gains and why they might have performed well.

2. **Underperformers (Losers)**:
   - List the assets/stocks/mutual funds that have underperformed relative to the rest of the portfolio.
   - Include percentage losses and potential reasons.

3. **Rebalancing Recommendations**:
   - Suggest actions to optimize portfolio allocation.
   - Highlight opportunities to reduce risk or improve returns.
   - Suggest diversification if the portfolio is heavily concentrated in certain sectors or asset classes.

4. **Risk Assessment**:
   - Provide a brief view of the portfolio's current risk profile (conservative, moderate, aggressive).
   - Highlight any high-risk concentrations or overexposure.

5. **Actionable Summary**:
   - Provide concise, easy-to-understand recommendations suitable for dashboard display.
   - Format clearly so each section can be displayed as a separate card/widget.

Please present the output in **human-readable, structured format**, keeping it suitable for quick review on a financial dashboard.
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
