from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def run_scraper():
    try:
        # ✅ Set Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # run without UI
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # ✅ Point to where Render installs chromium & chromedriver
        chrome_options.binary_location = "/usr/bin/chromium"
        service = Service("/usr/bin/chromedriver")

        # ✅ Launch driver
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get("https://www.linkedin.com/")  # Example target

        print("Page title:", driver.title)

        # Example: wait for login button
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            print("Page loaded successfully!")
        except TimeoutException:
            print("Timeout: Page did not load in time.")

        driver.quit()

    except Exception as e:
        print("Error while scraping:", str(e))


if __name__ == "__main__":
    run_scraper()
