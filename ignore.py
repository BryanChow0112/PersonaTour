import streamlit as st
import page1
import page2

# Initialize session state if not already done
if 'page' not in st.session_state:
    st.session_state.page = 'home'


# Navigation function
def navigate(page):
    st.session_state.page = page
    st.experimental_rerun()


# Main content based on the selected page
if st.session_state.page == 'home':
    st.title("Home Page")
    st.write("Welcome to the home page!")
    if st.button("Go to Page 1"):
        navigate('page1')
    if st.button("Go to Page 2"):
        navigate('page2')

elif st.session_state.page == 'page1':
    page1.show()

elif st.session_state.page == 'page2':
    page2.show()
