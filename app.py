import os
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Import your scraper
from scraper import scrape_keywords


def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Use Chromium binary in Render
    chrome_bin = "/usr/bin/chromium-browser"
    if os.path.exists(chrome_bin):
        chrome_options.binary_location = chrome_bin

    return webdriver.Chrome(options=chrome_options)


def main():
    st.title("LinkedIn Keyword Scraper")

    keywords = st.text_input("Enter keywords (comma-separated):")

    if st.button("Scrape"):
        if not keywords:
            st.error("Please enter some keywords.")
            return

        try:
            driver = get_driver()
            results = scrape_keywords(driver, keywords.split(","))
            driver.quit()

            st.success("Scraping complete!")
            for item in results:
                st.write(item)

        except Exception as e:
            st.error(f"Scraping failed: {str(e)}")


if __name__ == "__main__":
    main()
