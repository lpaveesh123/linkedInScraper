import streamlit as st
from scraper import scrape_keywords

st.title("🔍 LinkedIn Scraper")

keyword = st.text_input("Enter keyword to search:")
if st.button("Start Scraping"):
    if keyword.strip() == "":
        st.warning("⚠️ Please enter a keyword.")
    else:
        with st.spinner("Scraping in progress..."):
            result = scrape_keywords(keyword)
        st.success(result)
