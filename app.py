import streamlit as st
from scraper import scrape_keywords, save_df_to_excel

st.title("🔍 LinkedIn / Google Keyword Scraper")

# Input box for keywords
keywords = st.text_input("Enter keywords (comma separated):")

if st.button("Scrape"):
    if keywords.strip():
        keywords_list = [k.strip() for k in keywords.split(",")]
        st.write("Scraping started...")

        # Call scraper
        df = scrape_keywords(keywords_list)

        # Show results
        st.dataframe(df)

        # Save to Excel
        file_path = save_df_to_excel(df)

        with open(file_path, "rb") as f:
            st.download_button("Download Excel", f, "scraped_data.xlsx")
    else:
        st.error("⚠️ Please enter at least one keyword.")
