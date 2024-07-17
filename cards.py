import streamlit as st
from openai import OpenAI
import random

# OpenAI setup
api_key = st.secrets['OPENAI_API_KEY']
client = OpenAI(api_key=api_key)

# Methods for AI generation
def generate_description(prompt, client):
    description_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a travel expert. Generate a brief, engaging 50-word description for a travel package based on the given prompt."},
            {"role": "user", "content": f"{prompt}"}
        ],
        max_tokens=100,
        temperature=0.7
    )
    return description_response.choices[0].message.content

def generate_image_prompt(description):
    prompt_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Based on the travel package description, create a brief image prompt that captures the essence of the destination. The output should be within 100 characters."},
            {"role": "user", "content": f"{description}"}
        ],
        max_tokens=50,
        temperature=0.7
    )
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
        st.write(package['description'])
        st.write(f"Price: {package['price']}")
        if st.button(f"Book Now: {package['title']}", key=package['title']):
            st.write(f"Booking process for {package['title']} initiated!")

def travel_packages_tab():
    st.title("PersonaTour Travel Packages")

    # AI-generated package creation
    st.subheader("Create New Travel Package")
    with st.form("new_package"):
        destination = st.text_input("Destination")
        keywords = st.text_input("Keywords (e.g., beach, adventure, culture)")
        price = st.number_input("Price ($)", min_value=0, step=100)
        submitted = st.form_submit_button("Generate Package")

        if submitted:
            with st.spinner("Generating your travel package..."):
                prompt = f"Create a travel package for {destination} focusing on {keywords}"
                description = generate_description(prompt, client)
                image_prompt = generate_image_prompt(description)
                image_url = generate_image_url(image_prompt)

                new_package = {
                    "title": f"{destination} Adventure",
                    "description": description,
                    "price": f"${price}",
                    "image": image_url
                }

                # Add the new package to the existing packages
                if 'packages' not in st.session_state:
                    st.session_state.packages = []
                st.session_state.packages.append(new_package)
                st.success("New package created successfully!")

    # Display all travel packages
    st.subheader("Available Travel Packages")
    if 'packages' in st.session_state and st.session_state.packages:
        for package in st.session_state.packages:
            create_package_card(package)
            st.write("---")  # Separator between packages
    else:
        st.write("No packages available. Create a package above!")