import json
import time
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---------------- Chrome Driver Setup ----------------
def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--remote-debugging-port=9222")

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(300)
    driver.set_script_timeout(300)
    return driver

# ---------------- LinkedIn Login ----------------
def linkedin_login_with_cookies(driver, cookies_file="cookies.json"):
    """Login to LinkedIn using saved cookies"""
    try:
        driver.get("https://www.linkedin.com/")
        time.sleep(2)

        if not os.path.exists(cookies_file):
            raise FileNotFoundError(f"{cookies_file} not found. Make sure you have created it.")

        with open(cookies_file, "r") as f:
            cookies = json.load(f)

        for cookie in cookies:
            if "sameSite" in cookie and cookie["sameSite"] == "None":
                cookie["sameSite"] = "Strict"
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"⚠️ Skipping cookie: {cookie.get('name')}, error: {e}")

        driver.refresh()
        WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("✅ Logged in with cookies")

    except Exception as e:
        print(f"❌ Error during LinkedIn login: {e}")
        raise  # Re-raise to stop scraper if login fails

# ---------------- LinkedIn Post Scraper ----------------
def scrape_linkedin_posts(keyword, cookies_file="cookies.json", limit=5):
    """Scrape LinkedIn posts for a given keyword"""
    driver = get_driver()
    try:
        linkedin_login_with_cookies(driver, cookies_file)

        try:
            url = f"https://www.linkedin.com/search/results/content/?keywords={keyword}&origin=FACETED_SEARCH"
            driver.get(url)
            WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        except Exception as e:
            print(f"❌ Error loading search page: {e}")
            return pd.DataFrame()  # return empty DataFrame

        posts_data = []
        try:
            posts = driver.find_elements(By.CLASS_NAME, "update-components-text")[:limit]
            for idx, post in enumerate(posts, start=1):
                text = post.text.strip()
                posts_data.append({"Keyword": keyword, "Post #": idx, "Content": text})
        except Exception as e:
            print(f"❌ Error extracting posts: {e}")

        return pd.DataFrame(posts_data)

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return pd.DataFrame()

    finally:
        driver.quit()

# ---------------- Example Usage ----------------
if __name__ == "__main__":
    keyword = "Python"
    print("🚀 Scraping started...")
    df = scrape_linkedin_posts(keyword, limit=5)
    if df.empty:
        print("⚠️ No posts found or an error occurred.")
    else:
        print(df)
    print("✅ Scraping finished.")
