# scraper.py
"""
Lightweight LinkedIn scraper designed for Render + Streamlit deployments (no Selenium).
It prefers public search (Bing) to discover post/profile URLs and can optionally fetch
LinkedIn pages using cookies.json (li_at + JSESSIONID) if provided.

⚠️ Use responsibly. Scraping may violate site Terms. Prefer official APIs where possible.
"""

from __future__ import annotations
import json
import time
import random
import re
from typing import List, Dict, Optional, Tuple
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

DEFAULT_HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
}

BING_HEADERS = {
    **DEFAULT_HEADERS,
    "referer": "https://www.bing.com/",
}

def load_cookies(path: str) -> Dict[str, str]:
    """Load cookies.json (exported from a browser or created manually)."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Accept both list-of-dicts (Chrome export) or key/value dict.
    # Expect at least 'li_at' (auth token) and 'JSESSIONID'.
    cookies = {}
    if isinstance(data, list):
        for c in data:
            name = c.get("name")
            value = c.get("value")
            if name and value:
                cookies[name] = value
    elif isinstance(data, dict):
        cookies = data
    else:
        raise ValueError("Unsupported cookies.json format")

    return cookies

def make_session(cookies: Optional[Dict[str, str]] = None, headers: Optional[Dict[str, str]] = None) -> requests.Session:
    s = requests.Session()
    s.headers.update(headers or DEFAULT_HEADERS.copy())
    if cookies:
        # requests needs a cookie dict
        for k, v in cookies.items():
            s.cookies.set(k, v, domain=".linkedin.com")
        # LinkedIn often expects a CSRF token header mirroring JSESSIONID (strip quotes if present)
        jsid = cookies.get("JSESSIONID")
        if jsid:
            token = jsid.strip('"')
            s.headers["csrf-token"] = token
            s.headers["x-restli-protocol-version"] = "2.0.0"
            s.headers["x-li-lang"] = "en_US"
            s.headers["x-li-track"] = '{"clientVersion":"1.0.*","osName":"web"}'
    return s

def _random_pause(a: float = 0.7, b: float = 1.7):
    time.sleep(random.uniform(a, b))

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=6))
def _get(session: requests.Session, url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 15) -> requests.Response:
    r = session.get(url, headers=headers, timeout=timeout, allow_redirects=True)
    r.raise_for_status()
    return r

def bing_site_search(query: str, limit: int = 20) -> List[str]:
    """Use Bing to find public LinkedIn URLs (posts, activity, profiles, articles)."""
    session = make_session(headers=BING_HEADERS)
    urls = []
    count = 0
    page = 0
    # Bing paginates with 'first=' param (1-based); fetch in strides of 10
    while count < limit and page < 5:
        first = page * 10 + 1
        q = f"site:linkedin.com ({query})"
        url = f"https://www.bing.com/search?q={quote_plus(q)}&first={first}"
        resp = _get(session, url)
        soup = BeautifulSoup(resp.text, "lxml")
        for h2 in soup.select("li.b_algo h2 a"):
            href = h2.get("href")
            if href and "linkedin.com" in href:
                urls.append(href)
                count += 1
                if count >= limit:
                    break
        page += 1
        _random_pause()
    # de-dup preserving order
    seen = set()
    deduped = []
    for u in urls:
        if u not in seen:
            deduped.append(u)
            seen.add(u)
    return deduped[:limit]

def fetch_url_metadata(url: str, session: Optional[requests.Session] = None) -> Dict[str, str]:
    """Fetch simple metadata (title, description, og tags) from a URL."""
    s = session or make_session()
    try:
        resp = _get(s, url)
    except Exception as e:
        return {"url": url, "title": "", "description": "", "error": str(e)}

    soup = BeautifulSoup(resp.text, "lxml")
    title = (soup.title.string.strip() if soup.title and soup.title.string else "")

    # prefer Open Graph description
    og_desc = soup.find("meta", {"property": "og:description"})
    desc = og_desc["content"].strip() if og_desc and og_desc.get("content") else ""

    if not desc:
        meta_desc = soup.find("meta", {"name": "description"})
        if meta_desc and meta_desc.get("content"):
            desc = meta_desc["content"].strip()

    return {"url": url, "title": title, "description": desc, "error": ""}

def linkedin_keyword_harvest(keywords: List[str], per_keyword: int = 10,
                             cookies_path: Optional[str] = None) -> List[Dict[str, str]]:
    """
    High-level pipeline:
    1) Use Bing to discover LinkedIn links for each keyword.
    2) (Optional) Use LinkedIn cookies to fetch each URL (helps with gated content).
    3) Extract simple metadata.
    """
    results: List[Dict[str, str]] = []
    cookies = None
    session = None

    if cookies_path:
        try:
            cookies = load_cookies(cookies_path)
            session = make_session(cookies=cookies)
        except Exception as e:
            # fall back to no-auth session
            session = make_session()
            results.append({"url": "", "title": "", "description": "", "error": f"Failed to load cookies: {e}"})
    else:
        session = make_session()

    for kw in keywords:
        discovered = bing_site_search(kw, limit=per_keyword)
        for url in discovered:
            meta = fetch_url_metadata(url, session=session)
            meta["keyword"] = kw
            results.append(meta)
            _random_pause(0.3, 1.0)

    return results

if __name__ == "__main__":
    # Simple CLI for local testing
    import argparse, csv
    parser = argparse.ArgumentParser()
    parser.add_argument("--keywords", nargs="+", required=True, help="Keywords to search")
    parser.add_argument("--per-keyword", type=int, default=10)
    parser.add_argument("--cookies", type=str, default=None, help="Path to cookies.json")
    parser.add_argument("--out", type=str, default="results.csv")
    args = parser.parse_args()

    data = linkedin_keyword_harvest(args.keywords, args.per_keyword, args.cookies)
    import pandas as pd
    df = pd.DataFrame(data)
    df.to_csv(args.out, index=False, encoding="utf-8")
    print(f"Saved {len(df)} rows -> {args.out}")
