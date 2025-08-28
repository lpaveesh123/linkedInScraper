import json
import time
import os
import traceback
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---------------- Chrome Driver Setup ----------------
def get_driver():
    try:
        print("🟢 Setting up Chrome driver...")
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
        print("✅ Chrome driver ready")
        return driver
    except Exception as e:
        print(f"❌ Error in driver setup: {e}")
        traceback.print_exc()
        raise

# ---------------- LinkedIn Login ----------------
def linkedin_login_with_cookies(driver, cookies_file="cookies.json"):
    """Login to LinkedIn using saved cookies"""
    try:
        print("🟢 Navigating to LinkedIn...")
        driver.get("https://www.linkedin.com/")
        time.sleep(2)

        if not os.path.exists(cookies_file):
            raise FileNotFoundError(f"{cookies_file} not found. Please create it first.")

        print("🟢 Loading cookies...")
        try:
            with open(cookies_file, "r") as f:
                cookies = json.load(f)
        except Exception as e:
            print(f"❌ Failed to read {cookies_file}: {e}")
            traceback.print_exc()
            raise

        print("🟢 Adding cookies to browser...")
        for cookie in cookies:
            if "sameSite" in cookie and cookie["sameSite"] == "None":
                cookie["sameSite"] = "Strict"
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"⚠️ Skipping cookie {cookie.get('name')} -> {e}")

        print("🟢 Refreshing page to apply cookies...")
        driver.refresh()

        try:
            WebDriverWait(driver, 120).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            print("✅ Logged in with cookies")
        except Exception as e:
            print(f"❌ Login wait failed: {e}")
            traceback.print_exc()
            raise

    except Exception as e:
        print(f"❌ Error during LinkedIn login: {e}")
        traceback.print_exc()
        raise

# ---------------- LinkedIn Post Scraper ----------------
def scrape_linkedin_posts(keyword, cookies_file="cookies.json", limit=5):
    """Scrape LinkedIn posts for a given keyword"""
    driver = get_driver()
    try:
        linkedin_login_with_cookies(driver, cookies_file)

        print(f"🟢 Navigating to LinkedIn search for: {keyword}")
        try:
            url = f"https://www.linkedin.com/search/results/content/?keywords={keyword}&origin=FACETED_SEARCH"
            driver.get(url)
            WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            print("✅ Search page loaded")
        except Exception as e:
            print(f"❌ Error loading search page for {keyword}: {e}")
            traceback.print_exc()
            return pd.DataFrame()

        print("🟢 Extracting posts...")
        posts_data = []
        try:
            posts = driver.find_elements(By.CLASS_NAME, "update-components-text")[:limit]
            if not posts:
                print("⚠️ No posts found on page.")
            for idx, post in enumerate(posts, start=1):
                try:
                    text = post.text.strip()
                    posts_data.append({"Keyword": keyword, "Post #": idx, "Content": text})
                    print(f"✅ Extracted post #{idx}")
                except Exception as e:
                    print(f"⚠️ Could not extract post #{idx}: {e}")
        except Exception as e:
            print(f"❌ Error extracting posts: {e}")
            traceback.print_exc()

        return pd.DataFrame(posts_data)

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()
        return pd.DataFrame()

    finally:
        print("🟡 Closing browser...")
        driver.quit()

# ---------------- Example Usage ----------------
if __name__ == "__main__":
    keyword = "Python"
    print("🚀 Scraping started...")
    df = scrape_linkedin_posts(keyword, limit=5)
    if df.empty:
        print("⚠️ No posts found or an error occurred.")
    else:
        print("📊 Scraped Data:")
        print(df)
    print("✅ Scraping finished.")
