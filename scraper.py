import time
import json
import logging
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Setup logging
logging.basicConfig(
    filename="scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def load_cookies(driver, cookie_file="cookies.json"):
    """Load LinkedIn cookies from a file into the browser."""
    try:
        with open(cookie_file, "r") as f:
            cookies = json.load(f)

        driver.get("https://www.linkedin.com")  
        time.sleep(2)

        for cookie in cookies:
            cookie.pop("sameSite", None)
            driver.add_cookie(cookie)

        logging.info("✅ Cookies loaded successfully")
    except Exception as e:
        logging.error(f"❌ Error loading cookies: {e}")
        raise

def scrape_keywords(keyword, max_scrolls=3):
    """Scrape LinkedIn posts by keyword and save to Excel."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    try:
        load_cookies(driver)

        search_url = f"https://www.linkedin.com/search/results/content/?keywords={keyword}&origin=GLOBAL_SEARCH_HEADER"
        driver.get(search_url)
        logging.info(f"🔎 Searching for keyword: {keyword}")
        time.sleep(3)

        posts_data = []
        scrolls = 0

        while scrolls < max_scrolls:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            scrolls += 1

            posts = driver.find_elements(By.CSS_SELECTOR, "div.feed-shared-update-v2")
            logging.info(f"📌 Found {len(posts)} posts so far (scroll {scrolls})")

            for post in posts:
                try:
                    content = post.text.strip()
                    if content:
                        posts_data.append({"Keyword": keyword, "Post": content})
                except Exception:
                    continue

        if not posts_data:
            logging.warning("⚠️ No relevant posts found.")
            return None

        # Save to Excel
        df = pd.DataFrame(posts_data)
        filename = f"linkedin_posts_{keyword}.xlsx"
        df.to_excel(filename, index=False)
        logging.info(f"✅ Data saved to {filename}")
        return filename

    except Exception as e:
        logging.error(f"❌ Error in scrape_keywords: {e}")
        raise
    finally:
        driver.quit()
