import streamlit as st
import pandas as pd
from scraper import scrape_linkedin_posts

st.set_page_config(page_title="LinkedIn Scraper", layout="wide")

st.title("🔍 LinkedIn Scraper (Cookie Based)")

keywords_input = st.text_area("Enter keywords (one per line):")
start_button = st.button("Start Scraping")

if start_button and keywords_input.strip():
    keywords = [kw.strip() for kw in keywords_input.splitlines() if kw.strip()]
    
    all_results = []
    for kw in keywords:
        st.write(f"Scraping posts for **{kw}** ...")
        df = scrape_linkedin_posts(kw, limit=5)
        all_results.append(df)

    final_df = pd.concat(all_results, ignore_index=True)
    st.dataframe(final_df)

    # Download as CSV
    csv = final_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name="linkedin_posts.csv",
        mime="text/csv",
    )
