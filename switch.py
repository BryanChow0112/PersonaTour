import streamlit as st

# List of pages
pages = {
    "🎡 Scroll container": "./pages/2_🎡_Scroll_container.py",
    "❓ st.query⚊params": "./pages/3_❓_st.query⚊params.py",
    "📄 st.switch⚊pages": "./pages/4_📄_st.switch⚊pages.py",
    "🔗 Link column formatting": "./pages/5_🔗_Link_column_formatting.py"
}

# Dropdown to select the page
selected_page = st.selectbox("Select a page:", list(pages.keys()))

# Button to switch page
switch_page = st.button("Switch page")
if switch_page:
    # Switch to the selected page
    page_file = pages[selected_page]
    st.switch_page(page_file)
