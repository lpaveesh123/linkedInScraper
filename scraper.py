import pandas as pd
import time

# Dummy LinkedIn scraping logic
def scrape_linkedin(keywords):
    results = []
    for kw in keywords:
        time.sleep(1)  # Simulate delay
        results.append({
            "Keyword": kw,
            "Profile": f"John Doe ({kw})",
            "Job Title": f"{kw} at Example Corp",
            "Location": "Bangalore, India",
            "Profile URL": "https://www.linkedin.com/in/example"
        })
    df = pd.DataFrame(results)
    return df

def save_df_to_excel(df, filename="linkedin_data.xlsx"):
    df.to_excel(filename, index=False)
    return filename
