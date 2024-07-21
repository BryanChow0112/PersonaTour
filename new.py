import streamlit as st

context = """
You are an expert travel guide who can help people plan their trips. Suggest the following for answer:

1. Country, city
2. 

If they ask about something unrelated tell the users "OI! I am your tourguide not chat gpt". Only talk about tourism related queries.
        """


# Function to handle chatbot interactions
def run_chatbot():
    # Chatbot main
    st.title("PersonaTour guide")

    # Set a default model
    if "openai_model" not in st.session_state:
        # assigns value gpt-3.5-turbo to key openai_model in the session state dictionary
        st.session_state["openai_model"] = "gpt-4"

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    system_message = {"role": "system", "content": f'{context}'}

    st.session_state.messages.append(system_message)

    # Greeting
    with st.chat_message("assistant"):
        st.write("Hello 👋")

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:  # iterate through all messages\
        if message["content"] != context or message["role"] != "system":
            with st.chat_message(
                    message["role"]
            ):  # display below in an expander relative to the role
                st.markdown(message["content"] + " ~ " + message["role"])
                st.write(message)

    # Accept user input
    if prompt := st.chat_input("Ask me a travel query!"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
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


if __name__ == "__main__":
    run_chatbot()
