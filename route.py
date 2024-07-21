# Imports
import streamlit as st
import os
import googlemaps
from itertools import permutations
from polyline import decode
from urllib.parse import quote
import requests
import folium


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

    col1, col2 = container.columns(2)

    with col1:
        switch = container.toggle("**Mode of Transport**")    
        mode = 'walking' if switch else 'driving'

    with col2:
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
