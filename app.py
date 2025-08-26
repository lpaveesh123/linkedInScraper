import streamlit as st
from scraper import scrape_keywords

st.set_page_config(page_title="LinkedIn Scraper Demo", layout="centered")

st.title("🔎 LinkedIn Scraper Demo")

keyword = st.text_input("Enter a keyword:", "")

if st.button("Search"):
    if not keyword.strip():
        st.warning("⚠️ Please enter a keyword.")
    else:
        with st.spinner("Scraping posts..."):
            posts, error = scrape_keywords(keyword)

        if error:
            st.error(error)
        elif posts:
            st.success(f"✅ Found {len(posts)} posts for '{keyword}'")
            for idx, post in enumerate(posts, 1):
                st.write(f"**Post {idx}:** {post}")
        else:
            st.warning(f"No results for '{keyword}'.")
