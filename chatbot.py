import streamlit as st
from openai import OpenAI
from findplaces import api


def run_bot():
    # Runs the prompt and returns json
    places, user_input = api()

    # Initialize OpenAI client
    api_key = st.secrets['OPENAI_API_KEY']
    client = OpenAI(api_key=api_key)

    # st.write(places)

    # Define the system and user messages for the prompt
    top_ten_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role":
            "system",
            "content":
            ("You will take in a json file and output top 10 places by review in the format of json"
             )
        }, {
            "role": "user",
            "content": f'{places}'
        }],
        # max_tokens=
        # 5000,  # Increase max tokens to accommodate more detailed responses
        temperature=0,
        response_format={"type": "json_object"})

    top_ten = top_ten_response.choices[0].message.content

    # Define the system and user messages for the prompt
    description_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role":
            "system",
            "content":
            ("""You are an itinerary planner. You will take a JSON file as input and provide 'n' days itineraries where 'n' is the number of durations. If the durations = 2 days, then n=2 and make a 2 days itinerary. If no duration is specify, then make a 3 days itinerary.
            Each day should be unique, and if one location is in one day then it should not be in the rest. 
            If there are repeats of the same location in another day, suggest nearby places instead. 
            Ensure that each itinerary has a very short concise description, rating in starts, and address of each place listed in that order. 
            Do not include ratings for the itineraries themselves. If no rating put NA.

            Example output for "party, drink, 3 days, bali":
            Day 1: Arrive and Explore
            Morning:

            Arrival in Bali: Arrive at Ngurah Rai International Airport.
            Check-in: Drop your bags at your accommodation in Seminyak or Kuta.
            Afternoon:

            Lunch: Grab a quick bite at a local warung (small eatery) or café.
            Beach Time: Head to Double Six Beach or Kuta Beach to soak up some sun and relax.
            Evening/Night:

            Dinner: Enjoy dinner at a beachfront restaurant or a trendy spot in Seminyak.
            Nightlife: Explore the nightlife in Seminyak or Kuta. Here are some popular spots:
            Seminyak: Visit beach clubs like Ku De Ta, Potato Head Beach Club, or Mrs Sippy.
            Kuta: Check out clubs and bars along Jalan Legian and Poppies Lane.
            
            Day 2: Party and Chill
            Morning:

            Breakfast: Start your day with a hearty breakfast at a local café.
            Explore: Visit local markets or shops for souvenirs.
            Afternoon:

            Pool Party: If your accommodation has a pool party, join in for some daytime fun.
            Evening/Night:

            Dinner: Enjoy dinner at a nice restaurant or try some local Indonesian cuisine.
            Nightlife: Continue exploring the nightlife scene. Consider:
            Ubud: For a change of pace, visit Jazz Café or CP Lounge.
            Seminyak or Kuta: Return to your favorite clubs or try new ones.
            
            Day 3: Departure
            Morning:

            Relax: Take it easy in the morning, perhaps with a leisurely breakfast.
            Afternoon:

            Departure: Check out of your accommodation and head to the airport for your departure.
            This itinerary gives you a balance of partying, beach relaxation, and exploring local culture. Adjust it based on your preferences and the specific places you want to visit. Enjoy your time in Bali!
            """)
        }, {
            "role": "user",
            "content": f'{places}'
        }],
        # max_tokens=
        # 5000,  # Increase max tokens to accommodate more detailed responses
        temperature=1)

    # Extract and format the itinerary
    itinerary = description_response.choices[0].message.content

    # Display the formatted itinerary
    st.write("## Your Custom Itinerary")
    st.write(
        "Here is your custom itinerary. Each day is designed to provide a unique experience, featuring different places with detailed descriptions."
    )
    st.write(itinerary)

    # travel_packages_tab(itinerary)
