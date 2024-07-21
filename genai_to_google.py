import json
from pydantic.types import Json
import streamlit as st
import os
from openai import OpenAI
from prompts import genai_to_google_prompts


def prompt_user():
    st.title("Create your own itinerary!")

    # Create a text input for the user prompt
    user_input = st.text_input("Type your ideal vacation in a location", )

    return user_input


def generate_keywords(user_input):
    # Get key from os
    api_key = os.environ['OPENAI_API_KEY']
    client = OpenAI(api_key=api_key)

    system_content, user_example_content, assistant_example_content = genai_to_google_prompts(
    )

    description_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "system",
            "content": f'{system_content}'
        }, {
            "role": "user",
            "content": f'{user_example_content}'
        }, {
            "role": "assistant",
            "content": f'{assistant_example_content}'
        }, {
            "role": "user",
            "content": f"{user_input}"
        }],
        max_tokens=300,
        temperature=1.2,
        response_format={"type": "json_object"})
    return description_response.choices[0].message.content


def run_genai_to_google():
    user_input = prompt_user()
    keywords = generate_keywords(user_input)  #json format
    data = json.loads(keywords)
    return data


if __name__ == "__main__":
    data = run_genai_to_google()
    for keyword in data['keywords']:
        st.write(keyword)
