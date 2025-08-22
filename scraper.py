# scraper.py
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pyperclip
import re
from datetime import datetime

ADV_BASE = "https://www.linkedin.com/search/results/content/?keywords={kw}&origin=FACETED_SEARCH&sortBy=%22date_posted%22"

def build_urls(keywords):
    return [ADV_BASE.format(kw=kw.strip().replace(" ", "%20")) for kw in keywords if kw.strip()]

def make_driver(headless=True):
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)
    return driver

def scrape_keywords(keywords, scroll_rounds=5, sleep_between_scroll=2):
    urls = build_urls(keywords)
    driver = make_driver(headless=True)
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

    try:
        for search_url in urls:
            print(f"Navigating to {search_url}")
            driver.get(search_url)
            time.sleep(5)

            for _ in range(scroll_rounds):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(sleep_between_scroll)

            posts = driver.find_elements(By.CSS_SELECTOR, 'div.feed-shared-update-v2')

            for index, post in enumerate(posts):
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", post)
                    time.sleep(1)

                    # --- Extract Name and Company ---
                    name, company = "", ""
                    try:
                        name_block = post.find_element(By.CSS_SELECTOR, 'span.update-components-actor__title')
                        lines = name_block.text.strip().split('\n')
                        name_line = lines[0].strip()
                        company_line = lines[1].strip() if len(lines) > 1 else ""
                        name = re.sub(r'•\s*\d+(st|nd|rd|th)?\+?', '', name_line).strip()
                        if "-" in company_line:
                            company = company_line.split("-")[-1].strip()
                        elif " at " in company_line.lower():
                            parts = re.split(r"\sat\s", company_line, flags=re.IGNORECASE)
                            company = parts[-1].strip() if len(parts) > 1 else company_line
                        else:
                            company = company_line
                        if any(k in name.lower() for k in ["pvt","private","tech","llp","solutions","inc","group","corp"]):
                            company = name
                            name = ""
                    except:
                        try:
                            fallback_name = post.find_element(By.CSS_SELECTOR, 'span.feed-shared-actor__name').text.strip()
                            if any(k in fallback_name.lower() for k in ["pvt","private","llp","tech","solutions","inc","corp"]):
                                company = fallback_name
                                name = ""
                            else:
                                name = fallback_name
                        except:
                            name, company = "", ""

                    # --- Extract Post Link ---
                    post_link = ""
                    try:
                        menu_btn = post.find_element(By.CSS_SELECTOR, 'div.feed-shared-control-menu button')
                        driver.execute_script("arguments[0].click();", menu_btn)
                        time.sleep(1)
                        copy_btn = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located(
                                (By.XPATH, "//h5[normalize-space()='Copy link to post']/ancestor::div[@role='button']")
                            )
                        )
                        driver.execute_script("arguments[0].click();", copy_btn)
                        time.sleep(1)
                        driver.execute_script("window.getSelection().removeAllRanges();")
                        driver.find_element(By.TAG_NAME, "body").click()
                        time.sleep(0.5)
                        post_link = pyperclip.paste().strip()
                    except:
                        post_link = ""

                    # --- Extract Post Text ---
                    try:
                        post_text_elem = post.find_element(By.CSS_SELECTOR, 'div.feed-shared-update-v2__description span.break-words')
                        post_text = post_text_elem.text.lower().strip()
                    except:
                        post_text = ""

                    # --- Include / Exclude filters ---
                    if post_link not in seen_links and any(k in post_text for k in include_keywords) and not any(k in post_text for k in exclude_keywords):
                        all_results.append({"Name": name, "Company": company, "Post Link": post_link})
                        seen_links.add(post_link)

                except Exception as e:
                    print(f"[{index}] Skipping post: {e}")

    finally:
        driver.quit()
        print("Browser closed.")

    return pd.DataFrame(all_results, columns=["Name", "Company", "Post Link"])


def save_df_to_excel(df, prefix="linkedin_freelance_hybrid_posts"):
    if df.empty:
        return ""
    today = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    fname = f"{prefix}_{today}.xlsx"
    df.to_excel(fname, index=False)
    return fname
