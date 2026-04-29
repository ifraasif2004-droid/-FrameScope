import psycopg2
from dotenv import load_dotenv
import os
from newspaper import Article

load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT id, url FROM articles WHERE content IS NULL OR content = ''")
articles = cursor.fetchall()
cursor.close()
conn.close()

print(f"Scraping full text for {len(articles)} articles...")

for i, (article_id, url) in enumerate(articles):
    try:
        article = Article(url)
        article.download()
        article.parse()
        full_text = article.text

        if full_text:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE articles SET content = %s WHERE id = %s",
                (full_text, article_id)
            )
            conn.commit()
            cursor.close()
            conn.close()
            print(f"{i+1}/{len(articles)} ✓ Scraped: {url[:60]}...")
        else:
            print(f"{i+1}/{len(articles)} ✗ No text: {url[:60]}...")
    except Exception as e:
        print(f"{i+1}/{len(articles)} ✗ Error: {e}")

print("\nDone scraping!")