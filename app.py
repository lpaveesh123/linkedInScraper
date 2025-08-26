# app.py
from scraper import scrape_keywords
import pandas as pd

if __name__ == "__main__":
    # ✅ Replace with your LinkedIn cookies
    cookies = [
        {"name": "li_at", "value": "YOUR_COOKIE_HERE", "domain": ".linkedin.com"}
    ]

    keywords = ["AI", "Python", "Data Science"]
    df = scrape_keywords(keywords, cookies)

    print("\n--- DEMO SCRAPED POSTS ---\n")
    print(df)

    # Save small CSV
    df.to_csv("demo_posts.csv", index=False)
    print("\nSaved to demo_posts.csv")
