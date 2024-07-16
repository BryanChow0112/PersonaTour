import streamlit as st

page=st.session_state
'''if there is no page automatically calls main'''
if "currentPage" not in page:
    page["currentPage"]="main"
if page["currentPage"]=="main":
    st.header("You are at main page")
    changePage=st.button("nextPage")
    if changePage:
        page["currentPage"]="secondPage"
        st.experimental_rerun()
if page["currentPage"]=="secondPage":
    st.header("You are at Second page")
    back=st.button("move back")
    if back:
        ''' moving to main page '''
        page["currentPage"]="main"
        st.experimental_rerun()