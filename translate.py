import streamlit as st
from text_translation import extract_text_from_image, translate_text
from gtts import gTTS
import os


## LIMJUNYI
def translation():
    # Streamlit component for image upload
    uploaded_image = st.file_uploader(
        "Upload an image to translate the contents as you need",
        type=["jpg", "png", "jpeg"])

    # Streamlit component for language selection
    languages = {
        "English": "en",
        "Mandarin Chinese": "zh-CN",
        "Hindi": "hi",
        "Spanish": "es",
        "French": "fr",
        "Arabic": "ar",
        "Bengali": "bn",
        "Russian": "ru",
        "Portuguese": "pt",
        "Urdu": "ur"
    }

    full_name = st.selectbox("Translate to?", list(languages.keys()))
    target_language = languages[full_name]

    if uploaded_image is not None and target_language:
        # Display the original image
        st.image(uploaded_image, caption='Original Image')

        # Save the uploaded image to a temporary file
        with open("temp_image.jpg", "wb") as f:
            f.write(uploaded_image.getbuffer())

        # Extract text from the image
        extracted_text = extract_text_from_image("temp_image.jpg")

        # Translate the extracted text
        translated_text = translate_text(extracted_text, target_language)

        # Display the translated text
        st.write(f"Translated text ({full_name}):\n\n{translated_text}")

        # Delete the temporary image file after translation
        os.remove("temp_image.jpg")

        # Save text file and language
        with open("translated_text.txt", "w", encoding="utf-8") as f:
            f.write(translated_text)
        with open("language.txt", "w", encoding="utf-8") as f:
            f.write(target_language)

        return True


# Function to convert text to speech
def text_to_speech(text_file, language_file='en'):
    try:
        with open(text_file, 'r', encoding='utf-8') as f:
            text = f.read()

        with open(language_file, 'r', encoding='utf-8') as f:
            language = f.read()

        # Create a gTTS object
        tts = gTTS(text=text, lang=language, slow=False)

        # Save the audio file
        audio_file = "text-to-speech-output.mp3"
        tts.save(audio_file)

        return audio_file

    except Exception as e:
        return f"An error occurred while converting text to speech: {e}"


def translate():
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
