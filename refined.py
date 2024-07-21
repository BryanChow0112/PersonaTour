# Imports
import streamlit as st
from context import context
from cards import travel_packages_tab
from chatbot_function import run_chatbot, img_to_base64, translation, route, text_to_speech
from home import home
from chatbot import run_bot

### Set layout page to wide
# st.set_page_config(layout='wide')


def main():
    # Load and display sidebar image with glowing effect
    img_path = "images/logo2.jpg"
    img_base64 = img_to_base64(img_path)
    st.sidebar.markdown(
        f'<img src="data:image/png;base64,{img_base64}" class="cover-glow">',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")

    # Sidebar for Mode Selection
    # Create tabs
    tab_names = ["Home🏠", "TripChatbot🤖", "TripPlanner✈️", "TripTranslator🤌🏼"]
    selected_tab = st.sidebar.radio("Select a tab:", tab_names, index=0)
    # Display the st.info box if the checkbox is checked
    if selected_tab == "TripChatbot🤖":
        use_genai = st.sidebar.checkbox("With API", value=True)
    else:
        use_genai = False

    # Define content for each tab
    if selected_tab == "Home🏠":
        home()
    elif selected_tab == "TripChatbot🤖" and use_genai:
        run_bot()
    elif selected_tab == "TripChatbot🤖" and not use_genai:
        last_message = run_chatbot()
        if last_message:
            # st.write(last_message)
            travel_packages_tab(last_message)
    elif selected_tab == "TripPlanner✈️":
        st.title("TripPlanner✈️")
        route()
    elif selected_tab == "TripTranslator🤌🏼":
        st.title("TripTranslator🤌🏼")
        st.write(
            "Translate your trip to your language! Simply upload an image and select the target language."
        )
        st.write(
            'Your ultimate travel companion! Effortlessly translate languages on the go and make your travels smoother. Whether you’re navigating a new city, ordering food, looking up reviews or chatting with locals, TripTranslator ensures you understand and are understood. Translate your trip to your language with ease!'
        )

        translated = translation()  # Store the result of the translation

        if translated:  # Check if an image has been translated
            if st.button("text-to-speech"):
                st.write("It might take a while for tts to generate :(")
                audio = text_to_speech("translated_text.txt", "language.txt")
                st.audio(audio, format="audio/mp3")
        else:
            st.write(
                "***Please translate an image first to use the text-to-speech function.*** 🔊"
            )


if __name__ == "__main__":
    main()
