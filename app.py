import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# ---------- SCRAPER LOGIC ----------
def scrape_keywords(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Example: collect meta keywords + h1/h2/h3 tags
        keywords = []
        meta_keywords = soup.find("meta", attrs={"name": "keywords"})
        if meta_keywords and meta_keywords.get("content"):
            keywords.extend(meta_keywords["content"].split(","))

        for tag in soup.find_all(["h1", "h2", "h3"]):
            keywords.append(tag.get_text(strip=True))

        # Clean duplicates
        keywords = list(set([kw.strip() for kw in keywords if kw.strip()]))
        return keywords

    except Exception as e:
        return [f"Error scraping {url}: {str(e)}"]

def save_df_to_excel(df, filename="output.xlsx"):
    df.to_excel(filename, index=False)
    return filename

# ---------- STREAMLIT UI ----------
st.title("🔍 Simple Web Keyword Scraper")

url = st.text_input("Enter a URL to scrape:")

if st.button("Scrape"):
    if url:
        keywords = scrape_keywords(url)
        df = pd.DataFrame({"Keywords": keywords})

        st.write("### Extracted Keywords")
        st.dataframe(df)

        # Download option
        excel_file = save_df_to_excel(df)
        with open(excel_file, "rb") as f:
            st.download_button("Download Excel", f, file_name="keywords.xlsx")

    else:
        st.warning("Please enter a URL.")
