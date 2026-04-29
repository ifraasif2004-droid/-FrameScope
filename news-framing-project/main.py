from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

@app.get("/articles")
def get_articles():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            a.id, a.title, a.source_name, a.published_at, 
            a.query_used, a.country, a.description,
            af.frame_label as dominant_frame,
            at.sentiment_label, at.intensity_label
        FROM articles a
        LEFT JOIN article_frames af ON a.id = af.article_id AND af.is_dominant = true
        LEFT JOIN article_tone at ON a.id = at.article_id
        ORDER BY a.published_at DESC
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {
            "id": r[0],
            "title": r[1],
            "source_name": r[2],
            "published_at": str(r[3]),
            "topic": r[4],
            "country": r[5],
            "description": r[6],
            "dominant_frame": r[7],
            "sentiment_label": r[8],
            "intensity_label": r[9],
            "url_to_image": None
        }
        for r in rows
    ]

@app.get("/articles/{article_id}/frames")
def get_article_frames(article_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT frame_label, score, is_dominant 
        FROM article_frames 
        WHERE article_id = %s 
        ORDER BY score DESC
    """, (article_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {"frame_label": r[0], "score": round(r[1], 3), "is_dominant": r[2]}
        for r in rows
    ]

@app.get("/frames/distribution")
def get_frame_distribution():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT frame_label, COUNT(*) as count, AVG(score) as avg_score
        FROM article_frames
        WHERE is_dominant = true
        GROUP BY frame_label
        ORDER BY count DESC
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {"frame_label": r[0], "count": r[1], "avg_score": round(r[2], 3)}
        for r in rows
    ]

@app.get("/articles/{article_id}/tone")
def get_article_tone(article_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sentiment_score, sentiment_label, intensity_score, intensity_label
        FROM article_tone
        WHERE article_id = %s
    """, (article_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        return {"sentiment_score": 0, "sentiment_label": "neutral", 
                "intensity_score": 0, "intensity_label": "calm"}
    return {
        "sentiment_score": row[0],
        "sentiment_label": row[1],
        "intensity_score": row[2],
        "intensity_label": row[3]
    }

@app.get("/articles/{article_id}/content")
def get_article_content(article_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, description, content, url
        FROM articles WHERE id = %s
    """, (article_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        return {"content": ""}
    return {
        "title": row[0],
        "description": row[1],
        "content": row[2] or "",
        "url": row[3]
    }

@app.get("/articles/{article_id}/highlights")
def get_highlights(article_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, description, content 
        FROM articles WHERE id = %s
    """, (article_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        return {"highlights": {}}

    text = f"{row[0]} {row[1] or ''} {row[2] or ''}"

    FRAME_KEYWORDS = {
        "economic": ["economy", "gdp", "inflation", "trade", "market", "financial", "budget", "tax", "recession", "growth", "investment", "cost", "price", "wage", "job", "unemployment", "profit", "revenue", "debt", "deficit", "surplus", "export", "import", "currency", "dollar", "stock", "shares", "loan", "income", "salary", "spending", "wealth", "fiscal", "monetary", "banking", "credit", "subsidy", "tariff", "commerce", "business", "industry", "manufacturing", "retail"],
        "political": ["political", "election", "party", "parliament", "vote", "politician", "government", "president", "congress", "senate", "prime minister", "cabinet", "minister", "opposition", "coalition", "campaign", "ballot", "candidate", "administration", "white house", "downing street", "kremlin", "liberal", "conservative", "progressive", "populist", "nationalist", "socialist", "diplomacy", "foreign affairs", "summit", "bilateral", "nato", "democracy", "regime"],
        "crime and punishment": ["crime", "criminal", "arrest", "prison", "sentence", "murder", "theft", "violence", "police", "conviction", "penalty", "jail", "guilty", "shooting", "stabbing", "robbery", "fraud", "corruption", "trafficking", "gang", "weapon", "assault", "terrorism", "extremism", "bomb", "explosion", "hostage", "homicide", "cybercrime", "hacking", "smuggling", "suspect", "fugitive", "investigation", "warrant", "raid", "crackdown"],
        "health and safety": ["health", "disease", "medical", "hospital", "patient", "vaccine", "treatment", "safety", "mental health", "epidemic", "cancer", "doctor", "nurse", "surgery", "medication", "pharmaceutical", "diagnosis", "symptom", "infection", "virus", "pandemic", "outbreak", "quarantine", "public health", "healthcare", "therapy", "depression", "anxiety", "addiction", "emergency", "ambulance"],
        "security and defense": ["security", "military", "war", "defense", "threat", "attack", "weapon", "soldier", "terrorism", "conflict", "army", "nato", "missile", "nuclear", "intelligence", "surveillance", "border", "navy", "air force", "combat", "battlefield", "ceasefire", "invasion", "occupation", "resistance", "drone", "airstrike", "casualties", "refugee", "war crime", "cybersecurity", "espionage", "counterterrorism"],
        "morality": ["moral", "ethical", "right", "wrong", "value", "principle", "sin", "god", "religion", "faith", "virtue", "corrupt", "integrity", "honesty", "decency", "immoral", "conscience", "duty", "responsibility", "dignity", "respect", "shame", "guilt", "compassion", "empathy", "kindness", "evil", "truth", "lie", "deception", "trust", "betrayal", "loyalty", "sacred", "church", "mosque", "temple", "prayer"],
        "fairness and equality": ["fair", "equal", "justice", "discrimination", "inequality", "rights", "bias", "diversity", "inclusion", "gender", "race", "minority", "equity", "privilege", "oppression", "marginalized", "representation", "human rights", "civil rights", "freedom", "liberty", "suffrage", "protest", "activism", "lgbtq", "feminist", "racism", "sexism", "accessibility", "wage gap", "social justice", "systemic"],
        "cultural identity": ["culture", "identity", "tradition", "heritage", "nationality", "ethnic", "religion", "language", "community", "immigrant", "migration", "diaspora", "indigenous", "native", "assimilation", "integration", "multiculturalism", "nationalism", "patriotism", "history", "colonial", "slavery", "monument", "museum", "art", "literature", "music", "film", "food", "festival", "celebration", "stereotype", "belonging"],
        "public opinion": ["opinion", "poll", "survey", "public", "sentiment", "popularity", "approval", "support", "protest", "movement", "demand", "petition", "referendum", "voters", "citizens", "social media", "trending", "viral", "backlash", "criticism", "praise", "controversy", "debate", "perception", "attitude", "belief", "trust", "confidence", "satisfaction", "anger", "frustration", "hope", "fear", "awareness", "advocacy", "lobbying"],
        "policy prescription and evaluation": ["policy", "reform", "proposal", "plan", "strategy", "government", "regulation", "implement", "program", "initiative", "measure", "mandate", "executive order", "bill", "act", "legislation", "committee", "taskforce", "review", "evaluation", "assessment", "audit", "recommendation", "guideline", "standard", "protocol", "ministry", "department", "agency", "public policy", "social policy", "economic policy", "framework"],
        "capacity and resources": ["infrastructure", "resource", "capacity", "funding", "supply", "shortage", "energy", "water", "hospital", "school", "staff", "workforce", "electricity", "gas", "oil", "coal", "renewable", "solar", "wind", "nuclear", "transport", "road", "bridge", "railway", "airport", "internet", "broadband", "technology", "equipment", "facility", "public spending", "aid", "grant", "relief", "humanitarian", "manpower", "shortage", "underfunded"],
        "legality, constitutionality and jurisprudence": ["law", "legal", "court", "judge", "constitution", "ruling", "lawsuit", "legislation", "attorney", "trial", "verdict", "regulation", "statute", "amendment", "jurisdiction", "appeal", "conviction", "acquittal", "bail", "lawyer", "prosecutor", "defendant", "plaintiff", "evidence", "warrant", "supreme court", "civil law", "criminal law", "penalty", "fine", "sanction", "compliance", "illegal", "unconstitutional", "judicial", "tribunal"],
        "quality of life": ["quality", "living", "welfare", "community", "happiness", "lifestyle", "housing", "poverty", "standard", "wellbeing", "comfort", "satisfaction", "leisure", "recreation", "education", "literacy", "opportunity", "urban", "rural", "development", "progress", "clean", "environment", "pollution", "green", "sustainable", "parks", "transportation", "commute", "social services", "standard of living", "work life balance"],
        "external regulation and reputation": ["international", "global", "foreign", "diplomacy", "sanction", "reputation", "alliance", "treaty", "united nations", "trade deal", "bilateral", "multilateral", "wto", "imf", "world bank", "eu", "nato", "asean", "soft power", "influence", "credibility", "image", "ranking", "accountability", "transparency", "press freedom", "human rights report", "trade relations", "diplomatic ties", "embassy", "ambassador", "foreign aid", "peacekeeping"],
    }

    text_lower = text.lower()
    found = {}
    for frame, keywords in FRAME_KEYWORDS.items():
        matched = [kw for kw in keywords if kw in text_lower]
        if matched:
            found[frame] = matched[:5]

    return {"highlights": found}

@app.get("/map/data")
def get_map_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            a.country,
            af.frame_label,
            at.sentiment_label,
            at.intensity_label,
            COUNT(*) as article_count
        FROM articles a
        LEFT JOIN article_frames af ON a.id = af.article_id AND af.is_dominant = true
        LEFT JOIN article_tone at ON a.id = at.article_id
        WHERE a.country != 'Unknown' AND a.country IS NOT NULL
        GROUP BY a.country, af.frame_label, at.sentiment_label, at.intensity_label
        ORDER BY article_count DESC
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {
            "country": r[0],
            "dominant_frame": r[1],
            "sentiment": r[2],
            "intensity": r[3],
            "article_count": r[4]
        }
        for r in rows
    ]