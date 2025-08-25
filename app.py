import streamlit as st
from scraper import scrape_linkedin

st.title("🌐 LinkedIn Scraper (Demo)")

url = st.text_input("Enter LinkedIn Job URL:")

if st.button("Scrape"):
    if not url.strip():
        st.error("⚠️ Please enter a valid LinkedIn job URL.")
    else:
        with st.spinner("Scraping in progress..."):
            result = scrape_linkedin(url)

        if result["success"]:
            st.success(f"✅ Job Title: {result['job_title']}")
        else:
            st.error(f"🚨 Error: {result['error']}")
