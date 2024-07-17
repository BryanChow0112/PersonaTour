import googlemaps
from datetime import datetime
from itertools import permutations
from urllib.parse import quote
import requests
import folium
import streamlit as st


api_key = ''
gmaps = googlemaps.Client(key='api_key')

def calculate_route_distance(route, matrix):
    distance = 0
    for i in range(len(route) - 1):
        distance += matrix['rows'][route[i]]['elements'][route[i + 1]]['distance']['value']
    return distance

# Function to find optimal route
def find_optimal_route(source, destinations, mode='driving'):
    locations = [source] + destinations
    matrix = gmaps.distance_matrix(origins=locations, destinations=locations, mode=mode)
    location_indices = list(range(1, len(locations)))  # Exclude the source from permutations

    all_routes = permutations(location_indices)

    optimal_route = min(all_routes, key=lambda route: calculate_route_distance([0] + list(route) + [0], matrix))
    optimal_route_locations = [locations[i] for i in [0] + list(optimal_route) + [0]]
    return optimal_route_locations

def geocode_address(address, api_key):
    # URL encode the address using urllib.parse.quote
    encoded_address = quote(address)

    # Send a request to the Google Maps Geocoding API
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"
    response = requests.get(geocode_url)
    data = response.json()

    # Debug print statement to check the API response
    print(f"Geocoding response for '{address}': {data}")

    # Check the API response status and extract the coordinates
    if data['status'] == 'OK' and len(data['results']) > 0:
        lat = data['results'][0]['geometry']['location']['lat']
        lon = data['results'][0]['geometry']['location']['lng']
        return round(lat, 6), round(lon, 6)
    else:
        return None, None

def create_map():
    # Create the map with Google Maps
    map_obj = folium.Map(location=[3.1390, 101.6869], zoom_start=10)  # Centered on Kuala Lumpur
    return map_obj

def add_markers(map_obj, locations, popup_list=None):
    if popup_list is None:
        popup_list = [f"Location {i+1}" for i in range(len(locations))]
    for i in range(len(locations)):
        lat, lon = locations[i]
        popup = popup_list[i]
        folium.Marker([lat, lon], popup=popup, icon=folium.Icon(color='blue', icon='info-sign')).add_to(map_obj)
    return map_obj

if __name__ == "__main__":

    st.title("Optimal Route Finder")

    locations_input = st.text_input("Enter the locations separated by commas (e.g., Kuala Lumpur, Genting Highlands)")

    if st.button("Show Locations on Map"):
        locations = [loc.strip() for loc in locations_input.split(",")]

        # Geocode the locations
        geocoded_locations = [geocode_address(loc, api_key) for loc in locations]

        # Validate coordinates
        if any(coords is None for coords in geocoded_locations):
            invalid_locations = [locations[i] for i, coords in enumerate(geocoded_locations) if coords is None]
            st.error(f"Error geocoding addresses: {', '.join(invalid_locations)}")
        else:
            # Create map
            map_obj = create_map()
            add_markers(map_obj, geocoded_locations)

            # Display map
            st.subheader("Locations on Map")
            st.components.v1.html(map_obj._repr_html_(), height=600)


source = st.text_input("Enter the source location:")
destinations_input = st.text_area("Enter the destination locations (one per line):")

if st.button("Find Optimal Route"):
    if source and destinations_input:
        destinations = [dest.strip() for dest in destinations_input.split('\n') if dest.strip()]
        optimal_route = find_optimal_route(source, destinations)

        st.subheader("Optimal Route:")
        for idx, location in enumerate(optimal_route):
            st.write(f"{idx + 1}. {location}")
    else:
        st.error("Please enter both source and destinations.")