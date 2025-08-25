from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
import traceback


def scrape_linkedin(url: str):
    """
    Scrapes LinkedIn job title from a given URL.
    Returns a dictionary with success/failure message.
    """
    driver = None
    try:
        chrome_options = Options()
        # Deployment-friendly Chrome settings
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        # ✅ Do NOT use --user-data-dir to avoid conflicts in deployment
        service = Service()

        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)

        wait = WebDriverWait(driver, 15)
        job_title = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
        ).text

        return {"success": True, "job_title": job_title}

    except TimeoutException:
        return {"success": False, "error": "⏳ Timeout: Element not found within 15s."}
    except NoSuchElementException:
        return {"success": False, "error": "❌ Element not found on the page."}
    except WebDriverException as e:
        return {"success": False, "error": f"⚠️ WebDriver error: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"🔥 Unexpected error: {str(e)}\n{traceback.format_exc()}"}
    finally:
        if driver:
            driver.quit()
