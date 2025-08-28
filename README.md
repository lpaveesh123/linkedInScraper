# LinkedIn Scraper (Render + Streamlit)

A lightweight, Render-friendly LinkedIn scraping tool that:
- Finds LinkedIn URLs via public search (Bing) for given keywords
- Optionally uses your `cookies.json` (containing `li_at` and `JSESSIONID`) to fetch metadata behind light gating
- Runs as a Streamlit app (easy to deploy on Render Free plan)

> ⚠️ **Important:** Scraping may violate a website's Terms of Service. Use responsibly and for permitted purposes only.

## Files
- `app.py` — Streamlit UI
- `scraper.py` — scraping logic (requests + BeautifulSoup, no Selenium/Chrome)
- `cookies.sample.json` — template for your LinkedIn cookies
- `requirements.txt` — Python deps
- `render.yaml` — Render service definition

## Quick Start (Local)
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Render
1. Put these files in a public Git repo (GitHub/GitLab).
2. Create a **Web Service** on Render linked to that repo.
3. Render should auto-detect `render.yaml`. If not, set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
4. After deploy, open the app. Upload your `cookies.json` (or run without it).

## About `cookies.json`
- Minimal example (`cookies.sample.json`):
```json
{
  "li_at": "YOUR_LI_AT_TOKEN_HERE",
  "JSESSIONID": "ajax:YOUR_JSESSIONID_TOKEN_HERE"
}
```
- You may also upload a browser-exported cookie file (array of `{name,value,...}` objects). The app auto-detects both formats.

## CLI (Optional)
You can also run the scraper headless via CLI:
```bash
python scraper.py --keywords "Need Zoho partner" "React developer Mumbai" --per-keyword 10 --cookies cookies.json --out results.csv
```

## Notes
- This project avoids Selenium/Chrome to remain compatible with Render's Free plan.
- If you need deeper, dynamic data extraction, consider:
  - Official APIs and partnerships
  - Third-party search APIs
  - A headless-browser service (adds cost/complexity)
