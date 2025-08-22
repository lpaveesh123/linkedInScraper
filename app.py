import streamlit as st
import pandas as pd
from scraper import scrape_keywords, save_df_to_excel

st.set_page_config(page_title="Keyword Scraper", layout="wide")

st.title("🔍 Keyword Scraper Tool")

# Input
keyword = st.text_input("Enter a keyword:")
num_results = st.slider("Number of results", 5, 20, 10)

# Run button
if st.button("Scrape"):
    if keyword.strip() == "":
        st.warning("Please enter a keyword.")
    else:
        with st.spinner("Scraping in progress..."):
            df = scrape_keywords(keyword, num_results)

        st.success("Scraping completed!")
        st.dataframe(df, use_container_width=True)

        # Save and download
        excel_file = save_df_to_excel(df)
        with open(excel_file, "rb") as f:
            st.download_button(
                label="📥 Download Excel",
                data=f,
                file_name=excel_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
