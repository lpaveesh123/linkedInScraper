import pandas as pd
import requests
from bs4 import BeautifulSoup


def scrape_keywords(keyword: str, num_results: int = 10):
    """
    Scrape Google search results for the given keyword.
    (This is a demo version using requests + BeautifulSoup.
    For production, consider using SerpAPI or Google Custom Search API.)
    """
    results = []
    query = keyword.replace(" ", "+")
    url = f"https://www.google.com/search?q={query}"

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        search_results = soup.select("h3")[:num_results]

        for idx, item in enumerate(search_results, start=1):
            results.append({"Rank": idx, "Keyword": keyword, "Title": item.get_text()})
    else:
        results.append({"Rank": 1, "Keyword": keyword, "Title": "Failed to fetch"})

    return pd.DataFrame(results)


def save_df_to_excel(df: pd.DataFrame, filename: str = "results.xlsx"):
    """
    Save the DataFrame to an Excel file.
    """
    df.to_excel(filename, index=False)
    return filename
