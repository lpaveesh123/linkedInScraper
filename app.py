import streamlit as st
import pandas as pd
from scraper import scrape_linkedin, save_df_to_excel

st.set_page_config(page_title="LinkedIn Scraper", layout="wide")

st.title("🔎 LinkedIn Scraper Demo")

keywords_input = st.text_area("Enter keywords (comma separated):", "Python Developer, Data Scientist")

if st.button("Scrape"):
    keywords = [kw.strip() for kw in keywords_input.split(",") if kw.strip()]
    if not keywords:
        st.error("Please enter at least one keyword.")
    else:
        with st.spinner("Scraping LinkedIn... (demo mode)"):
            df = scrape_linkedin(keywords)

        st.success("✅ Scraping completed!")
        st.dataframe(df)

        file = save_df_to_excel(df)
        with open(file, "rb") as f:
            st.download_button("📥 Download Excel", f, file_name=file)
