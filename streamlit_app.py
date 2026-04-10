"""Agentic Streamlit app that routes prompts to tools, APIs, and a local database."""

from __future__ import annotations

import streamlit as st

from app.agentic import run_agent

st.set_page_config(page_title="Agentic Tool Runner", page_icon="🤖", layout="wide")
st.title("🤖 Agentic Prompt Runner")
st.caption("Enter a prompt and the agent will pick tools (API, DB, math, sentiment, time).")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        trace = message.get("trace")
        if trace:
            with st.expander("Tool trace"):
                for step in trace:
                    st.code(f"{step.tool_name}\n{step.output}")

prompt = st.chat_input("Try: 'save note: call mom', 'search notes mom', 'calculate 9*(3+2)', or 'tell me a joke'")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    tool_results = run_agent(prompt)
    response = "\n\n".join(result.output for result in tool_results)

    with st.chat_message("assistant"):
        st.markdown(response)
        with st.expander("Tool trace"):
            for result in tool_results:
                st.code(f"{result.tool_name}\n{result.output}")

    st.session_state.messages.append({"role": "assistant", "content": response, "trace": tool_results})
