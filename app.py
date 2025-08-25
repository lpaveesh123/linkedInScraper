import os
import streamlit as st
from scraper import scrape_keywords, save_df_to_excel

st.title("LinkedIn Scraper (Keyword-based Search)")

# Linux-compatible profile directory (inside Render container)
profile_dir = os.path.join(os.getcwd(), "chrome-profile")
os.makedirs(profile_dir, exist_ok=True)

keywords_input = st.text_area("Enter keywords (one per line):", height=150)
headless = st.checkbox("Run headless browser", value=True)

if st.button("Start Scraping"):
    if not keywords_input.strip():
        st.warning("⚠️ Please enter at least one keyword.")
    else:
        keywords = [kw.strip() for kw in keywords_input.splitlines() if kw.strip()]
        with st.spinner("🔍 Scraping LinkedIn posts, please wait..."):
            try:
                # Pass Linux-friendly profile dir
                df = scrape_keywords(keywords, headless=headless, profile_dir=profile_dir)

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
