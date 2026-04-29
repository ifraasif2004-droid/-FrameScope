import requests
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

GUARDIAN_KEY = os.getenv("GUARDIAN_API_KEY")

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

def fetch_guardian_articles(query, pages=3):
    articles = []
    for page in range(1, pages + 1):
        url = "https://content.guardianapis.com/search"
        params = {
            "q": query,
            "api-key": GUARDIAN_KEY,
            "show-fields": "bodyText,trailText,byline",
            "page-size": 50,
            "page": page,
            "order-by": "newest"
        }
        response = requests.get(url, params=params)
        data = response.json()

        if data["response"]["status"] != "ok":
            print(f"Error: {data}")
            break

        results = data["response"]["results"]
        articles.extend(results)
        print(f"  Fetched page {page} — {len(results)} articles")

    return articles

def save_guardian_articles(articles, query):
    conn = get_db_connection()
    cursor = conn.cursor()
    saved = 0

    for a in articles:
        fields = a.get("fields", {})
        try:
            cursor.execute("""
                INSERT INTO articles 
                    (title, description, content, source_name, author, url, published_at, query_used)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING
            """, (
                a.get("webTitle"),
                fields.get("trailText"),
                fields.get("bodyText"),
                "The Guardian",
                fields.get("byline"),
                a.get("webUrl"),
                a.get("webPublicationDate"),
                query
            ))
            saved += cursor.rowcount
        except Exception as e:
            print(f"Error saving: {e}")

    conn.commit()
    cursor.close()
    conn.close()
    print(f"  Saved {saved} new articles for '{query}'")

# Fetch articles for all our topics
queries = [
    "climate change",
    "economy",
    "crime",
    "health",
    "politics",
    "security",
    "immigration",
    "technology",
    "education",
    "human rights"
]

total = 0
for q in queries:
    print(f"\nFetching: {q}")
    articles = fetch_guardian_articles(q, pages=2)
    save_guardian_articles(articles, q)
    total += len(articles)

print(f"\nDone! Fetched {total} Guardian articles total.")