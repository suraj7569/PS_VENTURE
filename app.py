
import streamlit as st
from PIL import Image
import io
import os
from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.yfinance import YFinanceTools
from phi.tools.duckduckgo import DuckDuckGo


API_KEY = os.getenv("GROQ_API_KEY", "YOUR GROQ API KEY")


@st.cache_resource
def load_agents(api_key):
    # 1. Web Search Agent
    websearchagent = Agent(
        name='webagent',
        role='search the web for the information',
        model=Groq(id = 'llama-3.3-70b-versatile', api_key=api_key),
        tools = [DuckDuckGo()],
        instructions = ['Always include sources'],
        show_tools_calls = True,
        markdown = True,
    )

    # 2. Financial Agent
    finagent = Agent(
        name = 'finagent',
        model=Groq(id='llama-3.3-70b-versatile', api_key=api_key),
        tools = [YFinanceTools(stock_price=True, analyst_recommendations=True, stock_fundamentals=True, company_news=True)],
        instructions = 'use tables to display the data',
        shows_tools_calls = True,
        markdown=True,
    )

    # 3. Orchestrator Agent
    multiagent = Agent(
        team=[websearchagent, finagent],
        model=Groq(id = 'llama-3.3-70b-versatile', api_key=api_key),
        instructions = ['Always include sources','use tables to display the data'],
        show_tools_calls=True,
        markdown=True,
    )
    return multiagent


def run_streamlit_app():
    col1, col2 = st.columns([1, 4])

    with col1:
        try:
            st.image("mm.jpg", width=100)
        except FileNotFoundError:
            st.warning("Logo file not found. Please upload 'mm.jpg'.")
    with col2:
        st.title("💲PS Venture Financial Assistant")
        st.markdown("---") 

    # Load the agent only once
    agent = load_agents(API_KEY)

    # 1. Text Prompt Input
    user_prompt = st.text_area(
        "Your Query:",
        placeholder="e.g., Summarize analyst recommendations and share the latest news for TESLA stock",
        key="prompt_input"
    )

    # 2. Execution Button
    if st.button("Run Agent Query", key="run_button") and user_prompt:
        if "YOUR_GROQ_API_KEY_HERE" in API_KEY:
            st.error("Please replace 'YOUR_GROQ_API_KEY_HERE' with your actual Groq API key.")
            return

        st.subheader("Agent Response:")

        with st.spinner("Agent is thinking and coordinating..."):
          response_container = st.empty()
          full_response = ""

        try:

            response_generator = agent.run(user_prompt, stream=True)

            for run_response in response_generator:

                if run_response and run_response.content and isinstance(run_response.content, str):

                    full_response += run_response.content

                    response_container.markdown(full_response, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"An error occurred during agent execution: {e}")

if __name__ == "__main__":
    run_streamlit_app()
