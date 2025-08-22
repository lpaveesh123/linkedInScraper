# scraper.py
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def scrape_linkedin(email, password, keywords, max_results_per_keyword=5):
    """
    Scrape LinkedIn posts/jobs for the given keywords.
    Prints debug information to show login success and scraping progress.
    """
    options = Options()
    options.add_argument("--headless=new")  # run headless for Render
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    results = []

    try:
        print("Navigating to LinkedIn login page...")
        driver.get("https://www.linkedin.com/login")

        # Wait for login page
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        except TimeoutException:
            print("Login page did not load properly.")
            return pd.DataFrame()

        # Fill in credentials
        driver.find_element(By.ID, "username").send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        print("Submitted login form, waiting for login confirmation...")

        # Confirm login success
        time.sleep(5)
        if "feed" in driver.current_url:
            print("✅ Login successful!")
        else:
            print("❌ Login may have failed. Check credentials or 2FA.")
            return pd.DataFrame()

        # --- Scrape each keyword ---
        for kw in keywords:
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={kw.replace(' ', '%20')}"
            print(f"\nNavigating to search page for keyword: {kw}")
            driver.get(search_url)
            time.sleep(5)

            try:
                job_cards = driver.find_elements(By.CSS_SELECTOR, ".jobs-search-results__list-item")
                print(f"Found {len(job_cards)} job cards for keyword '{kw}'")
            except Exception as e:
                print(f"Error finding job cards for '{kw}': {e}")
                continue

            for idx, card in enumerate(job_cards[:max_results_per_keyword]):
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
                    print(f"Scraped [{idx+1}] {title} at {company}")
                except Exception as e:
                    print(f"Error extracting card [{idx+1}]: {e}")

    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        driver.quit()
        print("Browser closed.")

    if not results:
        print("No data scraped. Check login, keywords, or LinkedIn page structure.")
    else:
        print(f"\nTotal results scraped: {len(results)}")

    return pd.DataFrame(results)

def save_df_to_excel(df, prefix="linkedin_scraped"):
    """Save DataFrame to Excel with timestamp"""
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f"{prefix}_{today}.xlsx"
    if not df.empty:
        df.to_excel(filename, index=False)
        print(f"Data saved to {filename}")
    return filename
