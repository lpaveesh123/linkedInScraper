import pandas as pd
import time

# Dummy scraper (replace with real scraping logic)
def scrape_keywords(keywords):
    results = []
    for kw in keywords:
        # Simulate scraping delay
        time.sleep(1)
        results.append({
            "Keyword": kw,
            "Result": f"Sample result for {kw}"
        })
    df = pd.DataFrame(results)
    return df

def save_df_to_excel(df, filename="scraped_data.xlsx"):
    df.to_excel(filename, index=False)
    return filename
