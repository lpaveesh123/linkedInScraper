import streamlit as st
import pandas as pd
from scraper import scrape_keywords

st.set_page_config(page_title="LinkedIn Scraper", page_icon="🔍", layout="wide")
st.title("🔍 LinkedIn Scraper (Render Deployment)")

# Input box for keywords
keywords = st.text_area("Enter keywords (comma separated):")

# Headless is always True on Render (no UI browser available)
headless = True  

if st.button("Start Scraping"):
    if not keywords.strip():
        st.error("⚠️ Please enter at least one keyword before scraping.")
    else:
        try:
            keyword_list = [kw.strip() for kw in keywords.split(",") if kw.strip()]
            
            # Call scraper (Render safe: no profile_dir)
            df = scrape_keywords(keyword_list, headless=headless)

            if not df.empty:
                st.success("✅ Scraping completed successfully!")
                st.dataframe(df)

                # CSV download button
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Download results as CSV",
                    data=csv,
                    file_name="linkedin_results.csv",
                    mime="text/csv",
                )
            else:
                st.warning("⚠️ No data found for the given keywords.")

        except Exception as e:
            st.error(f"❌ Scraping failed: {str(e)}")
