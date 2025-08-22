import streamlit as st
from scraper import scrape_keywords, save_df_to_excel

st.title("LinkedIn Job Scraper 🚀")

# Let user type keywords (comma separated)
keywords_input = st.text_input("Enter keywords (comma separated)", "Python Developer, Data Analyst")

if st.button("Scrape Jobs"):
    keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
    
    if not keywords:
        st.error("⚠️ Please enter at least one keyword.")
    else:
        st.write(f"🔍 Scraping jobs for: {', '.join(keywords)}")
        df = scrape_keywords(keywords)
        
        if df.empty:
            st.warning("No jobs found.")
        else:
            st.dataframe(df)
            file = save_df_to_excel(df)
            st.success(f"✅ Jobs scraped and saved to {file}")
            st.download_button(
                label="📥 Download Excel",
                data=open(file, "rb").read(),
                file_name="jobs.xlsx"
            )
