import os
import streamlit as st
from scraper import scrape_keywords, save_df_to_excel
import tempfile

st.title("LinkedIn Scraper (Keyword-based Search)")

# -------------------------------
# Upload cookies.json
# -------------------------------
cookies_file = st.file_uploader("Upload cookies.json for LinkedIn login", type="json")

# -------------------------------
# Keywords input
# -------------------------------
keywords_input = st.text_area("Enter keywords (one per line):", height=150)
headless = st.checkbox("Run headless browser", value=True)

# -------------------------------
# Start scraping
# -------------------------------
if st.button("Start Scraping"):

    if not cookies_file:
        st.warning("⚠️ Please upload your cookies.json file.")
    elif not keywords_input.strip():
        st.warning("⚠️ Please enter at least one keyword.")
    else:
        # Save uploaded cookies to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
            tmp.write(cookies_file.getvalue())
            cookies_path = tmp.name

        keywords = [kw.strip() for kw in keywords_input.splitlines() if kw.strip()]

        with st.spinner("🔍 Scraping LinkedIn posts, please wait..."):
            try:
                df = scrape_keywords(keywords, headless=headless, cookies_path=cookies_path)

                if df.empty:
                    st.warning("⚠️ No relevant posts found.")
                else:
                    excel_path = save_df_to_excel(df)
                    if excel_path:
                        st.success(f"✅ Scraping completed! {len(df)} posts found.")
                        with open(excel_path, "rb") as f:
                            st.download_button(
                                label="📥 Download Excel",
                                data=f,
                                file_name=os.path.basename(excel_path),
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                        st.dataframe(df)
                    else:
                        st.warning("⚠️ Could not save Excel file, but data was scraped.")
            except Exception as e:
                st.error(f"❌ Scraping failed: {e}")
