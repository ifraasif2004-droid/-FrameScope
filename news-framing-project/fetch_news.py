import requests
import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime

# Load credentials
load_dotenv()
API_KEY = os.getenv("NEWS_API_KEY")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Connect to PostgreSQL
def get_db_connection():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    return conn

# Fetch articles from NewsAPI
def fetch_articles(query="politics", page_size=10):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "pageSize": page_size,
        "language": "en",
        "apiKey": API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()

    if data["status"] != "ok":
        print("Error fetching news:", data)
        return []

    print(f"Fetched {len(data['articles'])} articles for query: '{query}'")
    return data["articles"]

# Save articles to PostgreSQL
def save_articles(articles, query):
    conn = get_db_connection()
    cursor = conn.cursor()
    saved = 0

    for a in articles:
        try:
            cursor.execute("""
                INSERT INTO articles (title, description, content, source_name, author, url, published_at, query_used)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING
            """, (
                a.get("title"),
                a.get("description"),
                a.get("content"),
                a.get("source", {}).get("name"),
                a.get("author"),
                a.get("url"),
                a.get("publishedAt"),
                query
            ))
            saved += cursor.rowcount
        except Exception as e:
            print(f"Error saving article: {e}")

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Saved {saved} new articles to database")

# Run it for multiple topics
queries = ["climate change", "economy", "crime", "health", "politics"]

for q in queries:
    articles = fetch_articles(query=q, page_size=10)
    save_articles(articles, query=q)

print("\nDone! All articles saved.")