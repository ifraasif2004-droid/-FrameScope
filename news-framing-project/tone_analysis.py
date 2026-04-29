import psycopg2
from dotenv import load_dotenv
from textblob import TextBlob
import os

load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

# Intensity keywords - words that make tone sensational/alarmist
INTENSITY_KEYWORDS = [
    "crisis", "catastrophe", "disaster", "emergency", "urgent", "critical",
    "shocking", "alarming", "devastating", "horrific", "terrifying", "explosive",
    "unprecedented", "massive", "huge", "enormous", "extreme", "severe",
    "deadly", "fatal", "dangerous", "threatening", "warning", "alert",
    "breaking", "urgent", "dramatic", "chaos", "panic", "fear", "outrage",
    "scandal", "controversy", "clash", "war", "attack", "collapse", "failure",
    "worst", "record", "never before", "first time", "historic", "landmark"
]

def analyze_tone(text):
    if not text:
        return 0, "neutral", 0, "calm"
    
    # Sentiment using TextBlob (-1 to +1)
    blob = TextBlob(text)
    sentiment_score = round(blob.sentiment.polarity, 3)
    
    if sentiment_score > 0.05:
        sentiment_label = "positive"
    elif sentiment_score < -0.01:
        sentiment_label = "negative"
    else:
        sentiment_label = "neutral"
    
    # Intensity based on keyword count
    text_lower = text.lower()
    intensity_count = sum(text_lower.count(kw) for kw in INTENSITY_KEYWORDS)
    word_count = max(len(text.split()), 1)
    intensity_score = round(min(intensity_count / word_count * 100, 1.0), 3)
    
    if intensity_score > 0.05:
        intensity_label = "sensational"
    elif intensity_score > 0.02:
        intensity_label = "moderate"
    else:
        intensity_label = "calm"
    
    return sentiment_score, sentiment_label, intensity_score, intensity_label

def save_tone(article_id, sentiment_score, sentiment_label, intensity_score, intensity_label):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO article_tone 
            (article_id, sentiment_score, sentiment_label, intensity_score, intensity_label)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (article_id) DO UPDATE SET
            sentiment_score = EXCLUDED.sentiment_score,
            sentiment_label = EXCLUDED.sentiment_label,
            intensity_score = EXCLUDED.intensity_score,
            intensity_label = EXCLUDED.intensity_label
    """, (article_id, sentiment_score, sentiment_label, intensity_score, intensity_label))
    conn.commit()
    cursor.close()
    conn.close()

# Fetch articles
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT id, title, description, content FROM articles")
articles = cursor.fetchall()
cursor.close()
conn.close()

print(f"Analyzing tone for {len(articles)} articles...")

for i, (article_id, title, description, content) in enumerate(articles):
    text = f"{title} {description or ''} {content or ''}"
    sentiment_score, sentiment_label, intensity_score, intensity_label = analyze_tone(text)
    save_tone(article_id, sentiment_score, sentiment_label, intensity_score, intensity_label)
    print(f"{i+1}/{len(articles)} | {title[:45]}")
    print(f"         Sentiment: {sentiment_label} ({sentiment_score}) | Intensity: {intensity_label} ({intensity_score})")

print("\nDone! Tone analysis complete.")