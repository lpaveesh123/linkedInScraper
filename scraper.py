import json
import time
import os
import pandas as pd
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---------------- Chrome Driver Setup ----------------
def get_driver():
    options = Options()
    # comment out headless first for debugging
    # options.add_argument("--headless=new")
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
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("✅ Logged in with cookies")
        print("🔎 After login → URL:", driver.current_url)
        print("🔎 Page Title:", driver.title)

    except Exception:
        print("❌ Error during LinkedIn login:")
        traceback.print_exc()
        raise  # Stop scraper if login fails


# ---------------- LinkedIn Post Scraper ----------------
def scrape_linkedin_posts(keyword, cookies_file="cookies.json", limit=5):
    driver = get_driver()
    try:
        linkedin_login_with_cookies(driver, cookies_file)

        try:
            url = f"https://www.linkedin.com/search/results/content/?keywords={keyword}&origin=FACETED_SEARCH"
            driver.get(url)
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            print("🔎 Search page loaded → URL:", driver.current_url)
            print("🔎 Page Title:", driver.title)
        except Exception:
            print("❌ Error loading search page:")
            traceback.print_exc()
            return pd.DataFrame()

        posts_data = []
        try:
            # try multiple selectors because LinkedIn changes often
            posts = driver.find_elements(By.CLASS_NAME, "update-components-text")
            if not posts:
                posts = driver.find_elements(By.CSS_SELECTOR, "div.update-components-text.relative")

            print(f"🔎 Found {len(posts)} post elements")

            if not posts:
                # save page source for debugging
                with open("debug_page.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                print("⚠️ No posts found! Saved current page as debug_page.html")
            
            for idx, post in enumerate(posts[:limit], start=1):
                text = post.text.strip()
                posts_data.append({"Keyword": keyword, "Post #": idx, "Content": text})
        except Exception:
            print("❌ Error extracting posts:")
            traceback.print_exc()

        return pd.DataFrame(posts_data)

    except Exception:
        print("❌ Unexpected error:")
        traceback.print_exc()
        return pd.DataFrame()

    finally:
        driver.quit()


# ---------------- Example Usage ----------------
if __name__ == "__main__":
    keyword = "Python"
    print("🚀 Scraping started...")
    df = scrape_linkedin_posts(keyword, limit=5)
    if df.empty:
        print("⚠️ No posts found or an error occurred. Check debug logs above.")
    else:
        print(df)
    print("✅ Scraping finished.")
