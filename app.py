import streamlit as st
from scraper import scrape_keywords, save_df_to_excel

st.set_page_config(page_title="LinkedIn Scraper", layout="wide")

st.title("🔎 LinkedIn Scraper (Keyword-based Search)")

st.markdown("""
This tool scrapes LinkedIn posts based on your keywords.  
Enter one keyword per line and click **Start Scraping**.
""")

# Input for keywords
keywords_input = st.text_area("Enter keywords (one per line):", height=150)

# Option for headless browser
headless = st.checkbox("Run headless browser", value=True)

# Start scraping
if st.button("🚀 Start Scraping"):
    if not keywords_input.strip():
        st.warning("⚠️ Please enter at least one keyword.")
    else:
        keywords = [kw.strip() for kw in keywords_input.splitlines() if kw.strip()]
        with st.spinner("🔄 Scraping LinkedIn posts, please wait..."):
            try:
                df = scrape_keywords(
                    keywords,
                    headless=headless,
                    profile_dir="/opt/render/project/src/chrome-profile"  # Linux path for Render
                )

                if df.empty:
                    st.warning("⚠️ No relevant posts found.")
                else:
                    excel_path = save_df_to_excel(df)
                    st.success(f"✅ Scraping completed! {len(df)} posts found.")

                    # Download button
                    with open(excel_path, "rb") as f:
                        st.download_button(
                            label="📥 Download Excel",
                            data=f,
                            file_name="linkedin_posts.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

                    # Show DataFrame in app
                    st.dataframe(df)

            except Exception as e:
                st.error(f"❌ Scraping failed: {e}")
