import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager


def scrape_keywords(keywords, headless=True):
    """Scrape LinkedIn search results for a list of keywords"""

    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Initialize driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    data = []

    try:
        for keyword in keywords:
            url = f"https://www.linkedin.com/search/results/people/?keywords={keyword}"
            driver.get(url)
            time.sleep(3)  # allow page to load

            try:
                # Wait for results
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "entity-result__content"))
                )
                results = driver.find_elements(By.CLASS_NAME, "entity-result__content")

                for r in results:
                    try:
                        name = r.find_element(By.TAG_NAME, "span").text
                    except NoSuchElementException:
                        name = "N/A"

                    try:
                        occupation = r.find_element(By.CLASS_NAME, "entity-result__primary-subtitle").text
                    except NoSuchElementException:
                        occupation = "N/A"

                    data.append({
                        "Keyword": keyword,
                        "Name": name,
                        "Occupation": occupation
                    })

            except TimeoutException:
                print(f"[ERROR] Timeout while loading results for keyword: {keyword}")

    except Exception as e:
        print(f"[SCRAPER ERROR] {e}")

    finally:
        driver.quit()

    return pd.DataFrame(data)
