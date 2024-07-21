import streamlit as st
import base64

# Set page configuration for mobile-friendly layout
st.set_page_config(page_title="Mobile App Home", layout="centered")


# Function to load and encode an image to base64
def img_to_base64(img_path):
    with open(img_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


def home():
    # Custom CSS to improve mobile experience and add advertisement styling
    st.markdown("""
        <style>
        .main {
            padding: 1rem;
        }
        .block-container {
            padding: 1rem;
        }
        @media only screen and (max-width: 600px) {
            .main {
                padding: 0.5rem;
            }
            .block-container {
                padding: 0.5rem;
            }
        }
        .ad-image {
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 100%;
            max-width: 800px;
            border-radius: 10px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
        }
        .footer {
            text-align: center;
            padding: 10px;
        }
        </style>
        """,
                unsafe_allow_html=True)

    # Load images
    ad_img_path_1 = "images/logo.png"  # Replace with your first advertisement image path
    ad_img_path_2 = "images/a.jpg"  # Replace with your second advertisement image path
    ad_img_base64_1 = img_to_base64(ad_img_path_1)
    ad_img_base64_2 = img_to_base64(ad_img_path_2)

    # Store images and their corresponding hyperlinks in a list
    images = [{
        "src": f"data:image/jpeg;base64,{ad_img_base64_1}",
        "link": "https://www.youtube.com"
    }, {
        "src": f"data:image/jpeg;base64,{ad_img_base64_2}",
        "link": "https://www.google.com"
    }]

    # Initialize session state to store current image index
    if "current_image_index" not in st.session_state:
        st.session_state.current_image_index = 0

    # Header
    st.header("Welcome to the Mobile App")

    # Navigation buttons
    st.subheader("Navigation")
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("Home"):
            st.write("Navigating to Home")

    with col2:
        if st.button("Profile"):
            st.write("Navigating to Profile")

    with col3:
        if st.button("Settings"):
            st.write("Navigating to Settings")

    # Main content
    st.subheader("Main Content")
    st.write(
        "This is the main content area of the home interface. You can add more widgets and elements here."
    )

    # Image slider with hyperlinks
    current_image = images[st.session_state.current_image_index]
    st.markdown(
        f'<a href="{current_image["link"]}" target="_blank"><img src="{current_image["src"]}" class="ad-image"></a>',
        unsafe_allow_html=True,
    )

    # Navigation buttons below the image
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("◀"):
            st.session_state.current_image_index = (
                st.session_state.current_image_index - 1) % len(images)
    with col3:
        if st.button("▶"):
            st.session_state.current_image_index = (
                st.session_state.current_image_index + 1) % len(images)

    # Footer
    st.markdown("---")
    st.markdown("""
        <footer class="footer">
            <small>© 2024 Your Company</small>
        </footer>
        """,
                unsafe_allow_html=True)

    # Run the app with `streamlit run your_script.py`
