# app.py
import io
import json
import streamlit as st
import pandas as pd

from scraper import linkedin_keyword_harvest

st.set_page_config(page_title="LinkedIn Scraper (Render + Streamlit)", page_icon="🔎", layout="wide")

st.title("🔎 LinkedIn Scraper (Render + Streamlit, cookies.json optional)")
st.write(
    "This app discovers LinkedIn URLs via public search and optionally uses your cookies.json "
    "to fetch richer metadata. Use responsibly and respect Terms of Service."
)

with st.sidebar:
    st.header("Run Settings")
    per_keyword = st.slider("Results per keyword", min_value=3, max_value=50, value=10, step=1)
    st.caption("Tip: smaller batches are less likely to hit rate limits.")

    st.subheader("cookies.json (optional)")
    cookies_file = st.file_uploader("Upload cookies.json", type=["json"], accept_multiple_files=False, help="Include li_at and JSESSIONID if possible")

    st.subheader("Keyword Input")
    input_mode = st.radio("How will you provide keywords?", ["Textbox", "Upload .txt"])
    keywords = []

    if input_mode == "Textbox":
        text_blob = st.text_area("Enter one keyword per line", height=180, placeholder="e.g.\nNeed Zoho partner\nReact developer Mumbai\nData engineer remote")
        if text_blob.strip():
            keywords = [line.strip() for line in text_blob.splitlines() if line.strip()]
    else:
        txt = st.file_uploader("Upload a .txt file with one keyword per line", type=["txt"])
        if txt is not None:
            try:
                s = txt.read().decode("utf-8")
                keywords = [line.strip() for line in s.splitlines() if line.strip()]
            except Exception as e:
                st.error(f"Failed to read file: {e}")

    st.subheader("Export")
    export_name = st.text_input("CSV filename", value="linkedin_results.csv")

if st.button("Start Scraping", type="primary", use_container_width=True):
    if not keywords:
        st.warning("Please enter at least one keyword.")
        st.stop()

    cookies_path = None
    if cookies_file is not None:
        try:
            content = cookies_file.read().decode("utf-8")
            # Save uploaded cookies to a temp file in ephemeral disk
            cookies_path = "/tmp/cookies.json"
            with open(cookies_path, "w", encoding="utf-8") as f:
                f.write(content)
            st.success("cookies.json loaded.")
        except Exception as e:
            st.error(f"Failed to parse cookies.json: {e}")
            cookies_path = None

    with st.status("Scraping in progress...", expanded=True) as status:
        st.write(f"Keywords: {keywords}")
        st.write(f"Per keyword: {per_keyword}")
        data = linkedin_keyword_harvest(keywords, per_keyword=per_keyword, cookies_path=cookies_path)
        df = pd.DataFrame(data)
        st.write("Done. Preview below.")
        status.update(label="Finished", state="complete", expanded=False)

    st.dataframe(df, use_container_width=True)

    # Download button
    buf = io.BytesIO()
    df.to_csv(buf, index=False, encoding="utf-8")
    st.download_button("Download CSV", data=buf.getvalue(), file_name=export_name, mime="text/csv")

st.markdown("---")
st.caption("Note: This demo avoids headless browsers for reliability on Render. "
           "If you truly need Selenium, you'll have to provision a Chrome buildpack and tweak service settings, "
           "but requests-based fetching is generally simpler and cheaper.")
