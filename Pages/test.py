#imports
import streamlit as st
from openai import OpenAI

#Statics
api_key = st.secrets['OPENAI_API_KEY']
client = OpenAI(api_key=api_key)


#Methods
def generate_story(msg, client):
    story_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role":
                "system",
                "content":
                'You are a japanese best seller light novel writer. You will take user prompt and generate a 100 words short story for anime fans around age 20'
            },
            {
                "role": "user",
                "content": f'{msg}'
            },
            # {"role": "assistant", "content": ''},
            # {"role": "user", "content": ''}
        ],
        max_tokens=400,
        temperature=1.3)

    story = story_response.choices[0].message.content
    return story


def design_response(story, client):
    design_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role":
                "system",
                "content":
                "Based on the story given, you will design a detailed image prompt for the cover of this story. The image prompt should include the theme of the story with relevant colour, suitable for adults. The output should be within 100 characters."
            },  # system prompt
            {
                "role": "user",
                "content": f"{story}"
            }  # user prompt
        ],
        max_tokens=400,
        temperature=0.8)

    refined_story = design_response.choices[0].message.content
    return refined_story


def generate_image(refined_story):
    cover_response = client.images.generate(model='dall-e-2',
                                            prompt=f"{refined_story}",
                                            size="256x256",
                                            quality="standard",
                                            n=1)

    image_url = cover_response.data[0].url
    print(image_url)
    return image_url


# story = generate_story(msg, client)
# st.write(story)

# Insert containers separated into tabs:
tab1, tab2 = st.tabs(["Press Me!", "For the nerds"])
tab1.title("App that can change your life")

# # You can also use "with" notation:
# with tab1:
#   st.radio('Select one:', [1, 2])

with tab2.form('why this section cant be empty'):
    # st.write('This is for user to key in information')
    msg = st.text_input(label='Keywords to generate your story!')
    submitted = st.form_submit_button('Submit')
    if submitted:
        story = generate_story(msg, client)
        refined_story = design_response(story, client)
        image_url = generate_image(refined_story)
        st.image(image_url)

        # st.write(image_url)
