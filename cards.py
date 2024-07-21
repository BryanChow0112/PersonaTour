import streamlit as st
from openai import OpenAI
import random
import os

# OpenAI setup
api_key = 'sk-proj-a3z3g3hdXQzCaCCdcQYuT3BlbkFJQ7K1fDjjypZWIHxNDya7'
# api_key = os.environ['OPENAI_API_KEY']
client = OpenAI(api_key=api_key)

# Methods for AI generation
def generate_description(prompt, client):
    description_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role":
            "system",
            "content":
            "You are a travel expert. Generate a brief, engaging 60-word description for a travel package based on the given prompt."
        }, {
            "role": "user",
            "content": f"{prompt}"
        }],
        max_tokens=200,
        temperature=0.7)
    return description_response.choices[0].message.content


def generate_image_prompt(description):
    prompt_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role":
            "system",
            "content":
            "Based on the travel package description, create a brief image prompt that captures the essence of the destination. The output should be within 100 characters."
        }, {
            "role": "user",
            "content": f"{description}"
        }],
        max_tokens=50,
        temperature=0.7)
    return prompt_response.choices[0].message.content


def generate_image_url(image_prompt):
    image_response = client.images.generate(
        model="dall-e-2",
        prompt=f"{image_prompt}",
        size="256x256",
        quality="standard",
        n=1,
    )
    return image_response.data[0].url


# Function to create a package card
def create_package_card(package):
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(package['image'], use_column_width=True)
    with col2:
        st.subheader(package['title'])
        st.write(package['description'][:100] +
                 "...")  # Show a preview of the description
        st.write(f"Price: {package['price']}")

        if st.button(f"View Details: {package['title']}",
                     key=package['title']):
            show_package_details(package)


def show_package_details(package):
    st.subheader(package['title'])
    st.image(package['image'], use_column_width=True)
    st.write(package['description'])
    st.write(f"Price: {package['price']}")
    if st.button(f"Book Now: {package['title']}",
                 key=f"book_{package['title']}"):
        st.write(f"Booking process for {package['title']} initiated!")


def generate_package_from_message(message):
    # Extract destination and keywords from the message
    prompt = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role":
            "system",
            "content":
            "Extract the main destination and 2-3 keywords from the given travel message. Format the response as 'Destination: [destination], Keywords: [keyword1, keyword2, keyword3]'"
        }, {
            "role": "user",
            "content": message
        }],
        max_tokens=50,
        temperature=0.7)
    extraction = prompt.choices[0].message.content
    destination, keywords = extraction.split(", Keywords: ")
    destination = destination.split(": ")[1]

    # Generate package details
    description = generate_description(
        f"Create a travel package for {destination} focusing on {keywords}",
        client)
    image_prompt = generate_image_prompt(description)
    image_url = generate_image_url(image_prompt)
    price = f"${random.randint(500, 5000)}"  # Random price for demonstration

    return {
        "title": f"{destination} Adventure",
        "description": description,
        "price": price,
        "image": image_url
    }


def travel_packages_tab(last_message):
    st.title("PersonaTour Travel Packages")

    # Generate package from last chatbot message
    if last_message:
        with st.spinner(
                "Generating a travel package based on your conversation..."):
            new_package = generate_package_from_message(last_message)
            if 'packages' not in st.session_state:
                st.session_state.packages = []
            st.session_state.packages.append(new_package)
            st.success("New package created based on your conversation!")

    # Display all travel packages
    st.subheader("Available Travel Packages")
    if 'packages' in st.session_state and st.session_state.packages:
        for package in st.session_state.packages:
            create_package_card(package)
            st.write("---")  # Separator between packages
    else:
        st.write(
            "No packages available. Start a conversation to generate a package!"
        )
