import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def init_driver(headless=True, profile_dir=None):
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")

    if profile_dir:
        options.add_argument(f"user-data-dir={profile_dir}")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver


def scrape_keywords(keywords, headless=True, profile_dir=None):
    driver = init_driver(headless=headless, profile_dir=profile_dir)
    results = []

    try:
        for keyword in keywords:
            search_url = f"https://www.linkedin.com/search/results/content/?keywords={keyword}"
            driver.get(search_url)
            time.sleep(5)  # wait for page to load

            posts = driver.find_elements(By.CLASS_NAME, "update-components-text")
            for post in posts[:10]:  # limit to first 10 per keyword
                results.append({
                    "keyword": keyword,
                    "post": post.text.strip()
                })
    finally:
        driver.quit()

    df = pd.DataFrame(results)
    return df


def save_df_to_excel(df, filename="linkedin_results.xlsx"):
    df.to_excel(filename, index=False)
    return filename
