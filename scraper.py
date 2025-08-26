from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import time

ADV_BASE = "https://www.linkedin.com/search/results/content/?keywords={kw}&origin=GLOBAL_SEARCH_HEADER"

def scrape_keywords(keyword: str):
    try:
        # Selenium setup
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(service=Service(), options=options)

        driver.get(ADV_BASE.format(kw=keyword))
        wait = WebDriverWait(driver, 20)

        posts_data = []
        try:
            posts = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.feed-shared-update-v2")))
        except TimeoutException:
            driver.quit()
            return [], f"No posts found for '{keyword}'"

        # Fetch only first 3 posts
        for post in posts[:3]:
            try:
                text = post.text.strip().split("\n")[0]  # take first line
                posts_data.append(text)
            except Exception:
                posts_data.append("Error reading post")

        driver.quit()
        return posts_data, None

    except WebDriverException as e:
        return [], f"Selenium error: {str(e)}"
    except Exception as e:
        return [], f"Unexpected error: {str(e)}"
