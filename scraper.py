from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pandas as pd
import time

def scrape_keywords(keywords):
    service = Service("/usr/bin/chromedriver")  # path for Render container
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=service, options=options)

    results = []

    try:
        for keyword in keywords:
            url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}"
            driver.get(url)
            time.sleep(3)

            try:
                job_cards = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "base-card"))
                )
                for card in job_cards[:10]:  # scrape first 10 per keyword
                    try:
                        title = card.find_element(By.CLASS_NAME, "base-search-card__title").text
                        company = card.find_element(By.CLASS_NAME, "base-search-card__subtitle").text
                        location = card.find_element(By.CLASS_NAME, "job-search-card__location").text
                        results.append({
                            "Keyword": keyword,
                            "Job Title": title,
                            "Company": company,
                            "Location": location
                        })
                    except NoSuchElementException:
                        continue
            except TimeoutException:
                print(f"No jobs found for {keyword}")

    finally:
        driver.quit()

    return pd.DataFrame(results)

def save_df_to_excel(df, filename="jobs.xlsx"):
    df.to_excel(filename, index=False)
    return filename
