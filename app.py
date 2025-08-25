import streamlit as st
import pandas as pd
from scraper import scrape_keywords

st.title("🔍 LinkedIn Scraper")

keywords_input = st.text_area("Enter keywords (comma separated)", "Python Developer, Data Scientist")
keywords = [kw.strip() for kw in keywords_input.split(",") if kw.strip()]

if st.button("Scrape"):
    if not keywords:
        st.error("⚠ Please enter at least one keyword.")
    else:
        try:
            with st.spinner("Scraping in progress..."):
                df = scrape_keywords(keywords, headless=True)

            if not df.empty:
                st.success("✅ Scraping completed successfully!")
                st.dataframe(df)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("Download CSV", data=csv, file_name="linkedin_results.csv", mime="text/csv")
            else:
                st.warning("⚠ No results found. Try different keywords or login manually in development mode.")

        except Exception as e:
            st.error(f"❌ Scraping failed: {e}")
