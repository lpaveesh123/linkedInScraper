import streamlit as st
import pandas as pd
from scraper import scrape_linkedin, save_df_to_excel

st.set_page_config(page_title="LinkedIn Scraper", layout="wide")

st.title("🔎 LinkedIn Profile Scraper")

# Login details input
st.subheader("🔑 LinkedIn Login")
email = st.text_input("Email", type="default")
password = st.text_input("Password", type="password")

# Keyword input
st.subheader("📌 Search Keywords")
keywords_input = st.text_area("Enter keywords (one per line):", "Python Developer\nData Scientist")

if st.button("Scrape"):
    keywords = [kw.strip() for kw in keywords_input.split("\n") if kw.strip()]
    if not email or not password:
        st.error("⚠️ Please enter LinkedIn email and password.")
    elif not keywords:
        st.error("⚠️ Please enter at least one keyword.")
    else:
        with st.spinner("Scraping LinkedIn... (this may take time)"):
            try:
                df = scrape_linkedin(email, password, keywords)
                st.success("✅ Scraping completed!")

                st.dataframe(df)

                file = save_df_to_excel(df)
                with open(file, "rb") as f:
                    st.download_button("📥 Download Excel", f, file_name=file)

            except Exception as e:
                st.error(f"❌ Error: {e}")
