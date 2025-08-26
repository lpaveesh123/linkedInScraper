from flask import Flask, request, jsonify
from scraper import scrape_keywords

app = Flask(__name__)

@app.get("/scrape")
def scrape():
    """
    GET /scrape?keywords=python,selenium&max_posts=3
    Returns JSON with per-keyword status, posts, and message.
    """
    keywords = request.args.get("keywords", "")
    max_posts = request.args.get("max_posts", "3")

    try:
        max_posts = max(1, min(3, int(max_posts)))  # demo: clamp to 1..3
    except ValueError:
        max_posts = 3

    results = scrape_keywords(keywords_csv=keywords, max_posts=max_posts, cookies_path="cookies.json")
    return jsonify(results)

@app.get("/")
def root():
    return jsonify({"ok": True, "usage": "/scrape?keywords=python,selenium&max_posts=3"})

if __name__ == "__main__":
    # For local demo; in prod use a WSGI server (gunicorn/uvicorn)
    app.run(host="0.0.0.0", port=5000)
