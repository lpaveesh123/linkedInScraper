import os
import json
import streamlit as st
from scraper import scrape_keywords_with_cookies, save_df_to_excel

st.title("LinkedIn Scraper (Keyword-based Search)")

# Upload cookies.json
cookies_file = st.file_uploader("Upload cookies.json for LinkedIn login", type="json")

keywords_input = st.text_area("Enter keywords (one per line):", height=150)
headless = st.checkbox("Run headless browser", value=True)

if st.button("Start Scraping"):
    if not cookies_file:
        st.warning("⚠️ Please upload your cookies.json file.")
    elif not keywords_input.strip():
        st.warning("⚠️ Please enter at least one keyword.")
    else:
        try:
            # Load cookies from uploaded file
            cookies = json.load(cookies_file)
            
            keywords = [kw.strip() for kw in keywords_input.splitlines() if kw.strip()]
            
            with st.spinner("🔍 Scraping LinkedIn posts, please wait..."):
                # Call a scraper function that accepts cookies
                df = scrape_keywords_with_cookies(keywords, cookies=cookies, headless=headless)

                if df.empty:
                    st.warning("No relevant posts found.")
                else:
                    excel_path = save_df_to_excel(df)
                    st.success(f"✅ Scraping completed! {len(df)} posts found.")
                    
                    with open(excel_path, "rb") as f:
                        st.download_button(
                            label="📥 Download Excel",
                            data=f,
                            file_name=os.path.basename(excel_path),
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

                    st.dataframe(df)
        except Exception as e:
            st.error(f"❌ Scraping failed: {e}")
