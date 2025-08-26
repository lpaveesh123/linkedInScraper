import time
import json
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

COOKIES_FILE = "cookies.json"

def load_cookies():
    """Load LinkedIn cookies from file"""
    if not os.path.exists(COOKIES_FILE):
        raise FileNotFoundError("❌ cookies.json not found. Please add your LinkedIn cookies.")
    
    with open(COOKIES_FILE, "r") as f:
        try:
            cookies = json.load(f)
        except json.JSONDecodeError:
            raise ValueError("❌ cookies.json is not valid JSON.")
    
    if not cookies:
        raise ValueError("❌ cookies.json is empty.")
    return cookies


def init_driver():
    """Initialize Chrome WebDriver"""
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        service = Service()
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(60)
        return driver
    except WebDriverException as e:
        raise RuntimeError(f"❌ Failed to initialize Chrome driver: {e}")


def login_with_cookies(driver, cookies):
    """Login to LinkedIn using saved cookies"""
    driver.get("https://www.linkedin.com/")
    time.sleep(2)

    for cookie in cookies:
        if "sameSite" in cookie and cookie["sameSite"] == "None":
            cookie["sameSite"] = "Strict"
        try:
            driver.add_cookie(cookie)
        except Exception:
            pass  

    driver.refresh()
    time.sleep(3)


def scrape_keywords(keyword, max_posts=20):
    """Scrape LinkedIn posts for a given keyword"""
    driver = None
    try:
        cookies = load_cookies()
        driver = init_driver()
        login_with_cookies(driver, cookies)

        search_url = f"https://www.linkedin.com/search/results/content/?keywords={keyword}&origin=GLOBAL_SEARCH_HEADER"
        driver.get(search_url)

        posts_data = []
        wait = WebDriverWait(driver, 10)

        try:
            post_elements = wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "update-components-text"))
            )
        except TimeoutException:
            return []  # No posts found

        for idx, post in enumerate(post_elements[:max_posts]):
            try:
                text = post.text.strip()
                if text:
                    posts_data.append({"Keyword": keyword, "Post": text})
            except Exception:
                continue

        return posts_data

    except Exception as e:
        print(f"❌ Error in scrape_keywords: {e}")
        return None
    finally:
        if driver:
            driver.quit()


def save_to_excel(data, filename="output.xlsx"):
    """Save scraped data to Excel"""
    if not data:
        return "⚠️ No relevant posts found. Excel not created."
    
    try:
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)
        return f"✅ Data saved to {filename}"
    except Exception as e:
        return f"❌ Failed to save Excel: {e}"
