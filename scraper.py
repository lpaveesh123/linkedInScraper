# scraper.py
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_linkedin(email, password, keywords, max_results_per_keyword=5):
    """
    Scrape LinkedIn posts/jobs for the given keywords.
    Returns a pandas DataFrame with columns: Keyword, Title, Company, URL
    """
    # Set up Chrome options for headless execution
    options = Options()
    options.add_argument("--headless=new")  # headless for Render
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    results = []

    try:
        # --- Login ---
        driver.get("https://www.linkedin.com/login")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        driver.find_element(By.ID, "username").send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(5)  # wait for login

        # --- Search for each keyword ---
        for kw in keywords:
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={kw.replace(' ', '%20')}"
            driver.get(search_url)
            time.sleep(5)

            # Find job cards/posts
            job_cards = driver.find_elements(By.CSS_SELECTOR, ".jobs-search-results__list-item")

            for card in job_cards[:max_results_per_keyword]:
                try:
                    title = card.find_element(By.CSS_SELECTOR, ".job-card-list__title").text
                    company = card.find_element(By.CSS_SELECTOR, ".job-card-container__company-name").text
                    link = card.find_element(By.CSS_SELECTOR, "a").get_attribute("href")

                    results.append({
                        "Keyword": kw,
                        "Title": title,
                        "Company": company,
                        "URL": link
                    })
                except:
                    continue

    finally:
        driver.quit()

    return pd.DataFrame(results)

def save_df_to_excel(df, prefix="linkedin_scraped"):
    """Save DataFrame to Excel with timestamp"""
    if df.empty:
        return ""
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f"{prefix}_{today}.xlsx"
    df.to_excel(filename, index=False)
    return filename
