from openai import OpenAI
import streamlit as st
import re
from context import context
from cards import travel_packages_tab
import os

api_key = st.secrets['OPENAI_API_KEY']
client = OpenAI(api_key=api_key)


def run_chatbot():
    last_assistant_message = None
    st.title("Ideabot")

    # Initialize session state
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4"
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
        system_message = {"role": "system", "content": context}
        st.session_state.messages.append(system_message)

    # Display greeting
    with st.chat_message("assistant"):
        st.write("Hello 👋")

    # Display chat history
    for message in st.session_state.messages:
        if message["content"] != context or message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
            if message["role"] == "assistant":
                last_assistant_message = message["content"]

    # Chat input and response
    if prompt := st.chat_input("Ask me a travel query!"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[{
                    "role": m["role"],
                    "content": m["content"]
                } for m in st.session_state.messages],
                stream=True,
                max_tokens=500,
                temperature=1.2)
            response = st.write_stream(stream)
        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })
        last_assistant_message = response

    if len(st.session_state.messages) >= 4:
        # Add the "End Chat" button
        if st.button("End Chat and Generate Package"):
            return last_assistant_message

    # This return statement will only be reached if the button is not pressed
    return None
