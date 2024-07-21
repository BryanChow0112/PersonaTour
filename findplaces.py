import requests
import streamlit as st
from genai_to_google import run_genai_to_google


def fetch_place_details(api_key, place_id):
    details_url = (
        f"https://maps.googleapis.com/maps/api/place/details/json?"
        f"place_id={place_id}&fields=name,vicinity,rating,reviews,photos&key={api_key}"
    )
    details_response = requests.get(details_url)
    if details_response.status_code == 200:
        return details_response.json().get('result', {})
    return {}


def get_photo_url(photo_reference, api_key):
    photo_url = (
        f"https://maps.googleapis.com/maps/api/place/photo?"
        f"maxwidth=400&photoreference={photo_reference}&key={api_key}")
    return photo_url


def api():
    results = []
    json_data = run_genai_to_google()

    # Retrieve the API key from environment variables
    api_key = 'AIzaSyBKjWUZf6O_G7w5Jxo5KsO0H2NXEvzAfcM'

    if not api_key:
        st.error("API key not found")
        return results, json_data

    city_or_country = json_data.get('location', '')
    keywords = json_data.get('keywords', [])

    radius_km = 5
    radius_meters = radius_km * 1000

    geocode_url = (
        f"https://maps.googleapis.com/maps/api/geocode/json?address={city_or_country}&key={api_key}"
    )
    geocode_response = requests.get(geocode_url)
    if geocode_response.status_code != 200 or 'error_message' in geocode_response.json(
    ):
        st.error(
            f"Error: {geocode_response.json().get('error_message', 'Failed to get geocoding information.')}"
        )
        return results, json_data

    geocode_data = geocode_response.json()
    if 'results' not in geocode_data or len(geocode_data['results']) == 0:
        st.error("No geocoding results found.")
        return results, json_data

    location = geocode_data['results'][0]['geometry']['location']
    latitude, longitude = location['lat'], location['lng']

    all_places = []
    all_places_no_review = []

    for keyword in keywords:
        # Construct the Places API request URL
        places_url = (
            f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
            f"location={latitude},{longitude}&radius={radius_meters}&keyword={keyword}&key={api_key}"
        )

        # Make the Places API request
        response = requests.get(places_url)
        if response.status_code != 200:
            st.error(f"Error: {response.status_code}. Please try again later.")
            continue

        places = response.json()

        if 'results' not in places or len(places['results']) == 0:
            continue  # Skip if no places found

        # Fetch details for each place and add to all_places list
        for place in places['results']:
            place_details = fetch_place_details(api_key, place['place_id'])
            rating = place_details.get('rating', 'No rating available')
            reviews = place_details.get('reviews', [])
            photos = place_details.get('photos', [])

            photo_urls = [
                get_photo_url(photo['photo_reference'], api_key)
                for photo in photos[:1]
            ]  # Limit to 1 photo per place

            all_places.append({
                "name":
                place['name'],
                "address":
                place['vicinity'],
                "rating":
                rating,
                "reviews": [{
                    "author_name":
                    review.get('author_name', 'Anonymous'),
                    "text":
                    review.get('text', ''),
                    "rating":
                    review.get('rating', 'No rating')
                } for review in reviews[:5]],  # Limit reviews to 5
                "photos":
                photo_urls
            })

            all_places_no_review.append({
                "name": place['name'],
                "address": place['vicinity'],
                "rating": rating,
            })

    # Limit results to 3 initially
    limited_results = all_places[:3]

    # Display limited results
    show_all = st.button('Show All Results')
    results = all_places_no_review
    if show_all:
        results2 = all_places
    else:
        results2 = limited_results

    # Create columns for each place
    num_places = len(results2)
    num_columns = min(num_places, 3)  # Limit to 3 columns for layout purposes
    columns = st.columns(num_columns)

    for index, place in enumerate(results2):
        with columns[index % num_columns]:  # Distribute places across columns
            st.write(f"**{place['name']}**")
            st.write(f"Address: {place['address']}")
            st.write(f"Rating: {place['rating']}")

            if place['photos']:
                st.image(place['photos'][0],
                         use_column_width=True)  # Display the first photo

            if place['reviews']:
                with st.expander("Show Reviews"):
                    st.write("**Reviews:**")
                    for review in place['reviews']:  # Display reviews
                        author_name = review.get('author_name', 'Anonymous')
                        review_text = review.get('text', '')
                        review_rating = review.get('rating', 'No rating')
                        st.write(
                            f"**by @{author_name}**: {review_text} (Rating: {review_rating})"
                        )
            else:
                st.write("No reviews available.")

            st.write("---")

    return results, json_data
