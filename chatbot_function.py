# Imports
from openai import OpenAI
import streamlit as st
from context import context
from PIL import Image, ImageEnhance
import base64
from text_translation import extract_text_from_image, translate_text
import os
import googlemaps
from itertools import permutations
from polyline import decode
from urllib.parse import quote
import requests
import folium
from gtts import gTTS
import streamlit.components.v1 as components


# Setup OpenAI API
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

# Function to convert image to base64
def img_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


def load_and_enhance_image(image_path, enhance=False):
    """
    Load and optionally enhance an image.

    Parameters:
    - image_path: str, path of the image
    - enhance: bool, whether to enhance the image or not

    Returns:
    - img: PIL.Image.Image, (enhanced) image
    """
    img = Image.open(image_path)
    if enhance:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.8)
    return img


## LIMJUNYI
def capture_image():
    # Load the HTML page
    with open("webcam_component.html", "r") as f:
        html = f.read()

    # Use the HTML page as a Streamlit component
    data_url = components.html(html, height=600)

    # If a data URL was returned by the component
    if data_url and isinstance(data_url, str):
        # Remove the prefix from the data URL
        base64_str = data_url.split(",")[1]

        # Decode the base64 string to get the image data
        image_data = base64.b64decode(base64_str)

        # Open the image data with PIL
        image = Image.open(io.BytesIO(image_data))

        # Return the image
        return image
    else:
        st.error("No image captured or invalid data URL.")
        return None
        
def translation():
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

    # Streamlit component for image source selection
    image_source = st.selectbox("Choose image source", ["Upload", "Capture"])
    image = None
    
    if image_source == "Upload":
        # Streamlit component for image upload
        uploaded_image = st.file_uploader(
            "Upload an image to translate the contents as you need",
            type=["jpg", "png", "jpeg"])
        if uploaded_image is not None:
            image = Image.open(uploaded_image)
    elif image_source == "Capture":
        # Capture image from webcam
        image = capture_image()

    if image is not None and target_language:
        # Display the original image
        st.image(image, caption='Original Image')

        # Convert the image to RGB mode
        rgb_image = image.convert("RGB")

        # Save the image to a temporary file
        rgb_image.save("temp_image.jpg")

        # Extract text from the image
        extracted_text = extract_text_from_image("temp_image.jpg")

        # Translate the extracted text
        translated_text = translate_text(extracted_text, target_language)

        # Display the translated text
        st.write(f"Translated text ({full_name}): {translated_text}")

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


## NISHA
def route():
    api_key = os.getenv('GOOGLEMAPS_API_KEY')
    gmaps = googlemaps.Client(key=api_key)

    # Function to calculate route distance
    def calculate_route_distance(route, matrix):
        try:
            distance = 0
            for i in range(len(route) - 1):
                distance += matrix['rows'][route[i]]['elements'][route[
                    i + 1]]['distance']['value']
            return distance
        except KeyError as e:
            raise ValueError(
                "Invalid response from Google Maps API. Please check the input locations."
            ) from e

    # Function to find the optimal route
    def find_optimal_route(source, destinations):
        locations = [source] + destinations
        matrix = gmaps.distance_matrix(origins=locations,
                                       destinations=locations,
                                       mode='driving')

        if 'rows' not in matrix:
            raise ValueError(
                "Invalid response from Google Maps API. Please check the input locations."
            )

        location_indices = list(range(
            1, len(locations)))  # Exclude the source from permutations

        all_routes = permutations(location_indices)

        # Find the optimal route (single trip)
        try:
            optimal_route = min(all_routes,
                                key=lambda route: calculate_route_distance(
                                    [0] + list(route), matrix))
            optimal_route_locations = [
                locations[i] for i in [0] + list(optimal_route)
            ]
            return optimal_route_locations
        except ValueError as e:
            raise ValueError(
                "Unable to find an optimal route. Please check the input locations."
            ) from e

    # Function to geocode address
    def geocode_address(address, api_key):
        encoded_address = quote(address)
        geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"
        response = requests.get(geocode_url)
        data = response.json()

        if data['status'] == 'OK' and len(data['results']) > 0:
            lat = data['results'][0]['geometry']['location']['lat']
            lon = data['results'][0]['geometry']['location']['lng']
            return round(lat, 6), round(lon, 6)
        else:
            raise ValueError(
                f"Address '{address}' not recognized. Please enter a valid location."
            )

    # Function to create map
    def create_map():
        map_obj = folium.Map(zoom_start=5)
        return map_obj

    # Function to add markers to the map and adjust zoom
    def add_markers_and_zoom(map_obj, locations, popup_list=None):
        if popup_list is None:
            popup_list = [f"Location {i+1}" for i in range(len(locations))]

        lats = [loc[0] for loc in locations]
        lons = [loc[1] for loc in locations]

        for i in range(len(locations)):
            lat, lon = locations[i]
            popup = popup_list[i]
            folium.Marker([lat, lon],
                          popup=popup,
                          icon=folium.Icon(color='red',
                                           icon='info-sign')).add_to(map_obj)

        # Calculate bounds
        sw = [min(lats), min(lons)]
        ne = [max(lats), max(lons)]

        map_obj.fit_bounds([sw, ne])

        return map_obj

    def display_route_duration(optimal_route, mode):
        waypoints = optimal_route[
            1:-1]  # Intermediate destinations (excluding start and end)

        directions_result = gmaps.directions(
            origin=optimal_route[0],
            destination=optimal_route[-1],
            mode=mode,  # Use 'driving' or 'walking' as needed
            waypoints=waypoints,
            optimize_waypoints=True)
        return directions_result

    # Streamlit app layout
    st.title("Optimal Route Finder")

    container = st.container(border=True)
    switch = container.toggle("**Mode of Transport**")

    mode = 'walking' if switch else 'driving'

    container_html = f"""
        <div style="background-color: {'#362023' if mode == 'walking' else '#700548'}; 
                    padding: 10px; 
                    border-radius: 5px; 
                    text-align: center;
                    display: flex;
                    justify-content: center;
                    align-items: center;">
            <b>{'🚶‍♂️ Walking' if mode == 'walking' else '🚗 Driving'}</b>
        </div>
    """
    st.markdown(container_html, unsafe_allow_html=True)

    st.markdown("---")

    if 'destination_count' not in st.session_state:
        st.session_state['destination_count'] = 1

    if st.button("Add Destination"):
        st.session_state['destination_count'] += 1

    if st.button("Remove Destination"):
        if st.session_state['destination_count'] > 1:
            st.session_state['destination_count'] -= 1

    source = st.text_input("Enter the source location:")
    destinations = []

    for i in range(st.session_state['destination_count']):
        dest = st.text_input(f"Enter destination {i+1}:", key=f"dest_{i}")
        if dest:
            destinations.append(dest)

    if st.button("Find Optimal Route"):
        if source and destinations:
            try:
                optimal_route = find_optimal_route(source, destinations)

                st.subheader("Optimal Route:", divider='rainbow')
                for idx, location in enumerate(optimal_route):
                    st.write(f"{idx + 1}. {location}")

                # Geocode the optimal route locations for map display
                geocoded_locations = [
                    geocode_address(loc, api_key) for loc in optimal_route
                ]

                # Create map
                map_obj = create_map()
                add_markers_and_zoom(map_obj, geocoded_locations)

                # Use the optimal route to find the best walking route and time
                optimal_route_directions = display_route_duration(
                    optimal_route, mode)

                # Extract and display the duration for the optimal walking route
                if optimal_route_directions:
                    duration = sum(
                        leg['duration']['value']
                        for leg in optimal_route_directions[0]['legs'])

                    hours, remainder = divmod(duration, 3600)
                    minutes, _ = divmod(remainder, 60)
                    duration_text = f"{hours} hours, {minutes} minutes"

                    # Decode polyline points
                    polyline = optimal_route_directions[0][
                        'overview_polyline']['points']
                    polyline_points = decode(polyline)

                    # Add polyline to map
                    folium.PolyLine(polyline_points,
                                    color='blue',
                                    weight=2.5,
                                    opacity=1).add_to(map_obj)

                    map_html = map_obj._repr_html_()
                    st.components.v1.html(f"""
                        <div style="position: relative;">
                            <div style="position: absolute; top: 10px; right: 10px; padding: 10px; background-color: #4E4A59; color: white; border-radius: 5px; z-index: 1000;">
                                Time taken for the optimal route: {duration_text}
                            </div>
                            {map_html}
                        </div>
                        """,
                                          height=600,
                                          scrolling=True)
                else:
                    st.error(
                        "No route found for the optimal route. Please check your input locations."
                    )
            except ValueError as e:
                st.error(str(e))
        else:
            st.error("Please enter both source and destinations.")
