from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pandas as pd
import time
import re
import json
from datetime import datetime

ADV_BASE = "https://www.linkedin.com/search/results/content/?keywords={kw}&origin=FACETED_SEARCH&sortBy=%22date_posted%22"

# -------------------------------
# Load cookies
# -------------------------------
def load_cookies(driver, cookies_path="cookies.json"):
    try:
        with open(cookies_path, "r") as f:
            cookies = json.load(f)
        driver.get("https://www.linkedin.com")
        for cookie in cookies:
            cookie.pop("sameSite", None)
            driver.add_cookie(cookie)
        driver.refresh()
        time.sleep(3)

        if "feed" not in driver.current_url:
            print("⚠️ Cookies may be invalid, login failed.")
        else:
            print("✅ Cookies loaded, logged in successfully")
    except Exception as e:
        raise RuntimeError(f"Could not load cookies: {e}")

# -------------------------------
# Build URLs
# -------------------------------
def build_urls(keywords):
    urls = [ADV_BASE.format(kw=kw.strip().replace(" ", "%20")) for kw in keywords if kw.strip()]
    if not urls:
        raise ValueError("No keywords provided to build search URLs.")
    return urls

# -------------------------------
# Make driver
# -------------------------------
def make_driver(headless=True, chromedriver_path=None):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1280,2200")
        options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    try:
        if chromedriver_path:
            service = Service(executable_path=chromedriver_path)
            driver = webdriver.Chrome(service=service, options=options)
        else:
            driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        raise RuntimeError(f"Failed to start ChromeDriver: {e}")

# -------------------------------
# Scraper
# -------------------------------
def scrape_keywords(keywords, headless=True, chromedriver_path=None, scroll_rounds=5, sleep_between_scroll=2, cookies_path="cookies.json"):
    driver = make_driver(headless=headless, chromedriver_path=chromedriver_path)

    try:
        urls = build_urls(keywords)
        load_cookies(driver, cookies_path)

        all_results = []
        seen_links = set()

        include_keywords = [
            "freelancer", "hiring hybrid", "hybrid role", "remote or hybrid",
            "looking for freelancer", "freelance opportunity", "partner with us",
            "collaboration", "need freelance", "freelance partner", "zoho partner", "zoho consultant"
        ]
        exclude_keywords = [
            "full-time", "onsite", "in-office", "permanent", "work from office",
            "join full-time", "full time job"
        ]

        for search_url in urls:
            driver.get(search_url)
            time.sleep(5)

            # Scroll to load posts
            for _ in range(scroll_rounds):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(sleep_between_scroll)

            posts = driver.find_elements(By.CSS_SELECTOR, 'div.feed-shared-update-v2')
            if not posts:
                print(f"⚠️ No posts found for keyword URL: {search_url}")
                continue

            for index, post in enumerate(posts):
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", post)
                    time.sleep(1)

                    # --- Extract Name & Company ---
                    name, company = "", ""
                    try:
                        name_block = post.find_element(By.CSS_SELECTOR, 'span.update-components-actor__title')
                        full_text = name_block.text.strip()
                        lines = full_text.split('\n')
                        name_line = lines[0].strip()
                        company_line = lines[1].strip() if len(lines) > 1 else ""
                        name = re.sub(r'•\s*\d+(st|nd|rd|th)?\+?', '', name_line).strip()
                        company = company_line
                        if any(k in name.lower() for k in ["pvt","private","tech","llp","solutions","inc","group","corp"]):
                            company = name
                            name = ""
                    except:
                        pass

                    # --- Extract Post Link ---
                    try:
                        post_link_elem = post.find_element(By.CSS_SELECTOR, "a.app-aware-link")
                        post_link = post_link_elem.get_attribute("href")
                    except:
                        post_link = ""

                    # --- Extract Post Text ---
                    try:
                        post_text_elem = post.find_element(By.CSS_SELECTOR, 'div.feed-shared-update-v2__description span.break-words')
                        post_text = post_text_elem.text.lower().strip()
                    except:
                        post_text = ""

                    # --- Apply filters ---
                    if post_link and post_link not in seen_links:
                        if any(k in post_text for k in include_keywords) and not any(k in post_text for k in exclude_keywords):
                            all_results.append({"Name": name, "Company": company, "Post Link": post_link})
                            seen_links.add(post_link)

                except Exception as e:
                    print(f"[{index}] Skipping post due to error: {e}")

        return pd.DataFrame(all_results, columns=["Name", "Company", "Post Link"])

    except Exception as e:
        raise RuntimeError(f"Error in scrape_keywords: {e}")

    finally:
        driver.quit()

# -------------------------------
# Save to Excel
# -------------------------------
def save_df_to_excel(df, prefix="linkedin_freelance_hybrid_posts"):
    try:
        if df.empty:
            return ""
        today = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        fname = f"{prefix}_{today}.xlsx"
        df.to_excel(fname, index=False)
        return fname
    except Exception as e:
        raise RuntimeError(f"Error saving Excel file: {e}")
