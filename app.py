import streamlit as st
from scraper import scrape_keywords, save_df_to_excel

st.title("LinkedIn Scraper (Keyword-based Search)")

keywords_input = st.text_area("Enter keywords (one per line):", height=150)
headless = st.checkbox("Run headless browser", value=True)

if st.button("Start Scraping"):
    if not keywords_input.strip():
        st.warning("⚠️ Please enter at least one keyword.")
    else:
        keywords = [kw.strip() for kw in keywords_input.splitlines() if kw.strip()]
        with st.spinner("Scraping LinkedIn posts, please wait..."):
            try:
                df = scrape_keywords(keywords, headless=headless)
                if df.empty:
                    st.warning("No relevant posts found.")
                else:
                    excel_path = save_df_to_excel(df)
                    st.success(f"✅ Scraping completed! {len(df)} posts found.")
                    with open(excel_path, "rb") as f:
                        st.download_button("📥 Download Excel", f, file_name=excel_path)
                    st.dataframe(df)
            except Exception as e:
                st.error(f"❌ Scraping failed: {e}")
