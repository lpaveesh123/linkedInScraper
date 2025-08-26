# scraper.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd

ADV_BASE = "https://www.linkedin.com/search/results/content/?keywords={kw}&origin=FACETED_SEARCH"

def scrape_keywords(keywords, cookies):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    # Load LinkedIn and add cookies
    driver.get("https://www.linkedin.com/")
    for cookie in cookies:
        driver.add_cookie(cookie)

    results = []

    for kw in keywords:
        url = ADV_BASE.format(kw=kw.replace(" ", "%20"))
        driver.get(url)
        time.sleep(5)  # wait for page load

        posts = driver.find_elements(By.CLASS_NAME, "feed-shared-update-v2")[:3]  # only 3 posts

        for i, post in enumerate(posts, start=1):
            try:
                content = post.text[:300].replace("\n", " ")  # short preview
                results.append({"keyword": kw, "post_no": i, "content": content})
            except:
                continue

    driver.quit()

    df = pd.DataFrame(results)
    return df
