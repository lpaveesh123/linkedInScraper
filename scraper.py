import os
import json
import time
import logging
from typing import Dict, List
from urllib.parse import quote_plus

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
)

# -----------------------
# Logging
# -----------------------
LOG_PATH = os.path.join(os.path.dirname(__file__), "scraper.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler()
    ],
)
logger = logging.getLogger(__name__)

# -----------------------
# Driver init
# -----------------------
def _init_driver() -> webdriver.Chrome:
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,2000")
    # makes headless more stable in some hosts
    opts.add_argument("--disable-features=VizDisplayCompositor")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)

    # If your environment provides chromedriver on PATH, Service() with no args works.
    # Otherwise set: Service(executable_path="/path/to/chromedriver")
    driver = webdriver.Chrome(service=Service(), options=opts)
    driver.set_page_load_timeout(90)
    driver.set_script_timeout(90)
    return driver

# -----------------------
# Cookies (optional)
# -----------------------
def _maybe_load_cookies(driver: webdriver.Chrome, cookies_path: str = "cookies.json") -> bool:
    """
    Load cookies if cookies.json exists; returns True if loaded, False otherwise.
    Never raises on missing cookies (demo-friendly).
    """
    try:
        if not os.path.exists(cookies_path):
            logger.warning("cookies.json not found — continuing without cookies (public content only).")
            return False

        with open(cookies_path, "r", encoding="utf-8") as f:
            cookies = json.load(f)

        # Must be on the domain before adding cookies
        driver.get("https://www.linkedin.com/")
        time.sleep(2)

        for c in cookies:
            c.pop("sameSite", None)  # Selenium often dislikes explicit "None"
            try:
                driver.add_cookie(c)
            except Exception:
                # Skip any cookie that Selenium rejects
                pass

        driver.refresh()
        time.sleep(2)
        logger.info("Cookies loaded successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to load cookies: {e}", exc_info=True)
        return False

# -----------------------
# Helpers
# -----------------------
POST_SELECTORS = [
    # Common description block in LI feed/search
    "div.feed-shared-update-v2__description",
    "div.update-components-text",
    # Fallbacks
    "span.break-words",
    "div.feed-shared-update-v2",
]

def _extract_first_n_post_texts(driver: webdriver.Chrome, n: int = 3) -> List[str]:
    texts: List[str] = []

    # Try multiple selectors until we harvest enough
    for css in POST_SELECTORS:
        if len(texts) >= n:
            break

        try:
            elements = driver.find_elements(By.CSS_SELECTOR, css)
            for el in elements:
                if len(texts) >= n:
                    break
                txt = (el.text or "").strip()
                if not txt:
                    continue
                # de-dup near duplicates
                if any(txt[:80] in t or t[:80] in txt for t in texts):
                    continue
                # keep it short-ish for demo
                texts.append(" ".join(txt.split())[:600])
        except Exception:
            # If a selector fails in this run, just try next
            continue

    return texts[:n]

# -----------------------
# Core: scrape one keyword
# -----------------------
def scrape_keyword(keyword: str, max_posts: int = 3, cookies_path: str = "cookies.json") -> Dict:
    """
    Scrapes up to `max_posts` posts for a single keyword.
    Always returns a dict with: status, keyword, posts (list), message.
    """
    logger.info(f"Starting scrape for keyword: '{keyword}' (max {max_posts})")
    driver = None

    if not keyword or not keyword.strip():
        msg = "Keyword is empty."
        logger.warning(msg)
        return {"status": "error", "keyword": keyword, "posts": [], "message": msg}

    try:
        driver = _init_driver()
        _maybe_load_cookies(driver, cookies_path)

        # Navigate to content search (sorted by recency is often unstable; keep simple for demo)
        search_url = f"https://www.linkedin.com/search/results/content/?keywords={quote_plus(keyword)}&origin=GLOBAL_SEARCH_HEADER"
        driver.get(search_url)

        # Minimal wait for content to paint
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except TimeoutException:
            msg = "Page load timed out."
            logger.warning(msg)
            return {"status": "timeout", "keyword": keyword, "posts": [], "message": msg}

        # First read
        posts = _extract_first_n_post_texts(driver, n=max_posts)

        # If less than needed, scroll once or twice to coax lazy load
        scroll_attempts = 0
        while len(posts) < max_posts and scroll_attempts < 2:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            more = _extract_first_n_post_texts(driver, n=max_posts)
            # merge while keeping order & uniqueness
            seen = set()
            merged = []
            for t in posts + more:
                if t not in seen:
                    merged.append(t)
                    seen.add(t)
            posts = merged[:max_posts]
            scroll_attempts += 1

        if not posts:
            msg = f"No posts found for '{keyword}'."
            logger.info(msg)
            return {"status": "no_posts", "keyword": keyword, "posts": [], "message": msg}

        msg = f"Fetched {len(posts)} post(s) for '{keyword}'."
        logger.info(msg)
        return {"status": "ok", "keyword": keyword, "posts": posts, "message": msg}

    except TimeoutException as e:
        msg = f"Timeout while scraping '{keyword}': {e}"
        logger.error(msg, exc_info=True)
        return {"status": "timeout", "keyword": keyword, "posts": [], "message": msg}

    except WebDriverException as e:
        msg = f"Selenium/Chrome error for '{keyword}': {e}"
        logger.error(msg, exc_info=True)
        return {"status": "error", "keyword": keyword, "posts": [], "message": msg}

    except Exception as e:
        msg = f"Unexpected error for '{keyword}': {e}"
        logger.error(msg, exc_info=True)
        return {"status": "error", "keyword": keyword, "posts": [], "message": msg}

    finally:
        try:
            if driver:
                driver.quit()
        except Exception:
            pass

# -----------------------
# Batch: multiple keywords
# -----------------------
def scrape_keywords(keywords_csv: str, max_posts: int = 3, cookies_path: str = "cookies.json") -> Dict[str, Dict]:
    """
    Accepts comma-separated keywords; returns a dict keyed by keyword,
    each value is the result dict from scrape_keyword().
    """
    keywords = [k.strip() for k in (keywords_csv or "").split(",") if k.strip()]
    if not keywords:
        return {"": {"status": "error", "keyword": "", "posts": [], "message": "No keywords provided."}}

    results: Dict[str, Dict] = {}
    for kw in keywords:
        results[kw] = scrape_keyword(kw, max_posts=max_posts, cookies_path=cookies_path)
    return results
