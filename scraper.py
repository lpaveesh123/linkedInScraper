import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd


def linkedin_login_with_cookies(driver, cookies_file="cookies.json"):
    """Login to LinkedIn using saved cookies"""
    driver.get("https://www.linkedin.com/")
    time.sleep(2)

    # Load cookies
    with open(cookies_file, "r") as f:
        cookies = json.load(f)

    for cookie in cookies:
        if "sameSite" in cookie and cookie["sameSite"] == "None":
            cookie["sameSite"] = "Strict"
        driver.add_cookie(cookie)

    driver.refresh()
    time.sleep(3)
    print("✅ Logged in with cookies")


def scrape_linkedin_posts(keyword, cookies_file="cookies.json", limit=5):
    """Scrape LinkedIn posts for a given keyword"""
    options = Options()
    options.add_argument("--headless")  # comment this if you want browser window
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)

    try:
        linkedin_login_with_cookies(driver, cookies_file)

        url = f"https://www.linkedin.com/search/results/content/?keywords={keyword}&origin=FACETED_SEARCH"
        driver.get(url)
        time.sleep(5)

        posts_data = []
        posts = driver.find_elements(By.CLASS_NAME, "update-components-text")[:limit]

        for idx, post in enumerate(posts, start=1):
            text = post.text.strip()
            posts_data.append({"Keyword": keyword, "Post #": idx, "Content": text})

        return pd.DataFrame(posts_data)

    finally:
        driver.quit()
