import streamlit as st
from scraper import scrape_keywords, save_df_to_excel
import io

st.title("LinkedIn Scraper (Keyword-based Search)")

keywords_input = st.text_area("Enter keywords (one per line):", height=150)
headless = st.checkbox("Run headless browser", value=True)

if st.button("Start Scraping"):
    if not keywords_input.strip():
        st.warning("Please enter at least one keyword.")
    else:
        keywords = [kw.strip() for kw in keywords_input.splitlines() if kw.strip()]
        with st.spinner("Scraping LinkedIn posts, please wait..."):
            try:
                # Use None for profile_dir in server environments
                profile_dir = None  

                df = scrape_keywords(keywords, headless=headless, profile_dir=profile_dir)

                if df.empty:
                    st.warning("No relevant posts found.")
                else:
                    # Save to excel in memory
                    excel_buffer = io.BytesIO()
                    df.to_excel(excel_buffer, index=False, engine="openpyxl")
                    excel_buffer.seek(0)

                    st.success(f"Scraping completed! {len(df)} posts found.")

                    # Download button works with BytesIO
                    st.download_button(
                        "Download Excel",
                        data=excel_buffer,
                        file_name="linkedin_scraped.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                    st.dataframe(df)
            except Exception as e:
                st.error(f"Scraping failed: {e}")
