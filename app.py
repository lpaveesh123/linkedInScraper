import streamlit as st
from scraper import scrape_keywords, save_to_excel

st.set_page_config(page_title="LinkedIn Scraper", layout="centered")
st.title("🔎 LinkedIn Scraper")

keyword = st.text_input("Enter keyword to search on LinkedIn")
max_posts = st.number_input("Max posts to fetch", min_value=1, max_value=100, value=20)

if st.button("Start Scraping"):
    if not keyword.strip():
        st.error("⚠️ Please enter a keyword before scraping.")
    else:
        with st.spinner("Scraping posts..."):
            posts = scrape_keywords(keyword, max_posts)

        if posts is None:
            st.error("❌ An error occurred while scraping. Check logs.")
        elif len(posts) == 0:
            st.warning("⚠️ No relevant posts found for this keyword.")
        else:
            st.success(f"✅ Found {len(posts)} posts for '{keyword}'")
            msg = save_to_excel(posts, "output.xlsx")
            st.info(msg)
            if "saved to" in msg:
                with open("output.xlsx", "rb") as f:
                    st.download_button("📥 Download Excel", f, file_name="output.xlsx")
