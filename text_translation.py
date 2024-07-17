from PIL import Image
import pytesseract
from deep_translator import GoogleTranslator
import streamlit as st

# Function to extract text from an image
def extract_text_from_image(image_path):
    try:
        # Load the image
        img = Image.open(image_path)

        # Extract text using pytesseract
        text = pytesseract.image_to_string(img)

        return text
    except Exception as e:
        return f"An error occurred while extracting text from the image: {e}"

# Function to translate text
def translate_text(text, target_language):
    try:
        # Create a translator object
        translator = GoogleTranslator(source='auto', target=target_language)

        # Translate the text
        translated_text = translator.translate(text)

        return translated_text
    except Exception as e:
        return f"An error occurred while translating the text: {e}"
