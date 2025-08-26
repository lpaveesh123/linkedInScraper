import os
import json
import time
import logging
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# Setup logging
LOG_FILE = os.path.join(os.path.dirname(__file__), "scraper.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

COOKIES_FILE = os.path.join(os.path.dirname(__file__), "cookies.json")
SEARCH_URL = "https://www.linkedin.com/search/results/content/?keywords={kw}&origin=FACETED_SEARCH"

def load_cookies(driver):
    """Load cookies into the Selenium session."""
    if not os.path.exists(COOKIES_FILE):
        logging.error("Cookies file not found.")
        return False
    
    try:
        with open(COOKIES_FILE, "r") as f:
            cookies = json.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)
        logging.info("Cookies loaded successfully.")
        return True
    except Exception as e:
        logging.error(f"Could not load cookies: {e}")
        return False


def scrape_keywords(keyword):
    """Scrape LinkedIn posts for a given keyword."""
    logging.info(f"Starting scrape for {keyword}")

    try:
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(service=Service(), options=chrome_options)
        driver.set_page_load_timeout(60)

        driver.get("https://www.linkedin.com")
        time.sleep(2)

        if not load_cookies(driver):
            driver.quit()
            return f"❌ Failed: Could not load cookies."

        driver.get(SEARCH_URL.format(kw=keyword))
        time.sleep(5)

        try:
            posts = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.update-components-text"))
            )
        except TimeoutException:
            driver.quit()
            logging.warning(f"No relevant posts found for keyword: {keyword}")
            return f"⚠️ No relevant posts found for '{keyword}'."

        if not posts:
            driver.quit()
            logging.warning(f"No relevant posts found for keyword: {keyword}")
            return f"⚠️ No relevant posts found for '{keyword}'."

        results = [post.text.strip() for post in posts if post.text.strip()]
        driver.quit()

        if not results:
            logging.warning(f"No relevant posts extracted for keyword: {keyword}")
            return f"⚠️ No relevant posts extracted for '{keyword}'."

        # Save results to Excel
        filename = f"results_{keyword}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(os.path.dirname(__file__), filename)
        pd.DataFrame({"Posts": results}).to_excel(filepath, index=False)
        logging.info(f"Scraping completed. Saved to {filename}")

        return f"✅ Scraping completed for '{keyword}'. File saved: {filename}"

    except WebDriverException as e:
        logging.error(f"Selenium error: {e}")
        return f"❌ Selenium error: {str(e)}"

    except Exception as e:
        logging.error(f"Error in scrape_keywords: {e}")
        return f"❌ Error: {str(e)}"
