import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager


def scrape_keywords(keywords, headless=True):
    """
    Scrape LinkedIn posts for given keywords.
    Works in headless mode for cloud publishing (Render, etc.).
    """
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    # Use webdriver_manager to auto-install ChromeDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    data = []
    try:
        for keyword in keywords:
            driver.get(f"https://www.linkedin.com/search/results/content/?keywords={keyword}")
            time.sleep(5)

            posts = driver.find_elements(By.CLASS_NAME, "entity-result__summary")
            for post in posts:
                try:
                    text = post.text.strip()
                    data.append({"Keyword": keyword, "Post": text})
                except Exception:
                    continue

    except (NoSuchElementException, TimeoutException) as e:
        print(f"Error while scraping: {e}")
    finally:
        driver.quit()

    return pd.DataFrame(data)


def save_df_to_excel(df):
    """Save DataFrame to Excel and return filename"""
    filename = "linkedin_scraper_results.xlsx"
    df.to_excel(filename, index=False)
    return filename
