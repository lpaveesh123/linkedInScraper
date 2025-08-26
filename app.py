import streamlit as st
import os
import logging
from scraper import scrape_keywords

# Setup logging for Streamlit
logging.basicConfig(
    filename="scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

st.title("🔎 LinkedIn Scraper")
st.write("Enter a keyword and scrape LinkedIn posts.")

keyword = st.text_input("Keyword", "")
max_scrolls = st.slider("Scroll Depth", 1, 10, 3)

if st.button("Start Scraping"):
    if not keyword.strip():
        st.error("⚠️ Please enter a keyword first.")
    else:
        try:
            st.info(f"Starting scrape for **{keyword}**...")
            result_file = scrape_keywords(keyword, max_scrolls=max_scrolls)

            if result_file:
                st.success("✅ Scraping completed successfully!")
                with open(result_file, "rb") as f:
                    st.download_button(
                        label="📥 Download Excel",
                        data=f,
                        file_name=result_file,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            else:
                st.warning("⚠️ No relevant posts found for this keyword.")

        except Exception as e:
            st.error("❌ An error occurred while scraping. Check logs.")
            logging.error(f"Streamlit Error: {e}")
