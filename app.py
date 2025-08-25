import streamlit as st
from scraper import scrape_keywords, scrape_linkedin_with_login, save_df_to_excel

st.set_page_config(page_title="LinkedIn Scraper", layout="wide")
st.title("🔎 LinkedIn Scraper")

# Mode selection
mode = st.radio("Choose mode:", ["Local (Reuse Chrome Profile)", "Server (Email/Password Login)"])

keywords_input = st.text_area("📌 Enter keywords (one per line):", "Python Developer\nData Scientist")

profile_dir = None
email, password = None, None

if mode == "Local (Reuse Chrome Profile)":
    st.info("✅ Local Mode: Will reuse your Chrome login session. Make sure you are logged in to LinkedIn in that Chrome profile.")
    profile_dir = st.text_input("Enter Chrome Profile Path:", r"C:\Users\<YourUser>\AppData\Local\Google\Chrome\User Data")

elif mode == "Server (Email/Password Login)":
    st.info("🌐 Server Mode: Will log in with LinkedIn credentials each run.")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

if st.button("🚀 Start Scraping"):
    keywords = [kw.strip() for kw in keywords_input.splitlines() if kw.strip()]

    if not keywords:
        st.error("⚠️ Please enter at least one keyword.")
    else:
        with st.spinner("Scraping LinkedIn... Please wait ⏳"):
            try:
                if mode == "Local (Reuse Chrome Profile)":
                    df = scrape_keywords(keywords, profile_dir=profile_dir)
                else:
                    if not email or not password:
                        st.error("⚠️ Please enter LinkedIn email and password.")
                        st.stop()
                    df = scrape_linkedin_with_login(email, password, keywords)

                if df.empty:
                    st.warning("⚠️ No relevant posts found. Try different keywords.")
                else:
                    st.success(f"✅ Scraping completed! {len(df)} posts found.")
                    st.dataframe(df)

                    file = save_df_to_excel(df)
                    if file:
                        with open(file, "rb") as f:
                            st.download_button("📥 Download Excel", f, file_name=file)
                    else:
                        st.error("⚠️ No data to save.")

            except Exception as e:
                st.error(f"❌ Error during scraping: {e}")
