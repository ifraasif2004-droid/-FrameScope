import psycopg2
from dotenv import load_dotenv
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

# Keyword-based frame scoring
FRAME_KEYWORDS = {
    "economic": [
        "economy", "gdp", "inflation", "trade", "market", "financial", "budget", "tax",
        "recession", "growth", "investment", "cost", "price", "wage", "job", "unemployment",
        "profit", "loss", "revenue", "debt", "deficit", "surplus", "export", "import",
        "currency", "dollar", "interest rate", "stock", "shares", "bonds", "loan",
        "mortgage", "income", "salary", "earnings", "spending", "consumption", "poverty",
        "wealth", "fiscal", "monetary", "banking", "credit", "subsidy", "tariff",
        "commerce", "business", "enterprise", "startup", "corporation", "industry",
        "manufacturing", "retail", "supply chain", "economic growth", "gdp growth"
    ],
    "capacity and resources": [
        "infrastructure", "resource", "capacity", "funding", "supply", "shortage",
        "energy", "water", "hospital", "school", "staff", "workforce", "electricity",
        "gas", "oil", "coal", "renewable", "solar", "wind", "nuclear", "pipeline",
        "transport", "road", "bridge", "railway", "airport", "port", "internet",
        "broadband", "technology", "equipment", "facility", "budget allocation",
        "investment in", "public spending", "aid", "grant", "donation", "charity",
        "relief", "humanitarian", "support system", "manpower", "personnel"
    ],
    "morality": [
        "moral", "ethical", "right", "wrong", "value", "principle", "sin", "god",
        "religion", "faith", "virtue", "corrupt", "integrity", "honesty", "decency",
        "immoral", "unethical", "conscience", "duty", "responsibility", "dignity",
        "respect", "shame", "guilt", "repentance", "forgiveness", "compassion",
        "empathy", "kindness", "evil", "good", "justice", "injustice", "truth",
        "lie", "deception", "manipulation", "trust", "betrayal", "loyalty",
        "sacred", "blasphemy", "church", "mosque", "temple", "prayer", "belief"
    ],
    "fairness and equality": [
        "fair", "equal", "justice", "discrimination", "inequality", "rights", "bias",
        "diversity", "inclusion", "gender", "race", "minority", "majority", "equity",
        "privilege", "oppression", "marginalized", "representation", "affirmative",
        "human rights", "civil rights", "freedom", "liberty", "democracy", "vote",
        "suffrage", "protest", "activism", "movement", "campaign", "reform",
        "lgbtq", "women", "feminist", "racism", "sexism", "ageism", "ableism",
        "accessibility", "opportunity", "wage gap", "pay gap", "glass ceiling"
    ],
    "legality, constitutionality and jurisprudence": [
        "law", "legal", "court", "judge", "constitution", "ruling", "lawsuit",
        "legislation", "attorney", "trial", "verdict", "regulation", "statute",
        "amendment", "jurisdiction", "appeal", "conviction", "acquittal", "bail",
        "lawyer", "prosecutor", "defendant", "plaintiff", "testimony", "evidence",
        "warrant", "subpoena", "injunction", "habeas corpus", "due process",
        "supreme court", "federal court", "civil law", "criminal law", "penalty",
        "fine", "sanction", "compliance", "enforcement", "illegal", "unconstitutional",
        "rights violation", "legal challenge", "judicial", "legislative", "executive"
    ],
    "policy prescription and evaluation": [
        "policy", "reform", "proposal", "plan", "strategy", "government", "regulation",
        "implement", "program", "initiative", "measure", "directive", "mandate",
        "executive order", "bill", "act", "law passed", "legislation passed",
        "government plan", "five year", "action plan", "roadmap", "framework",
        "committee", "taskforce", "review", "evaluation", "assessment", "audit",
        "recommendation", "guideline", "standard", "protocol", "procedure",
        "administration", "ministry", "department", "agency", "bureau", "office",
        "public policy", "social policy", "economic policy", "foreign policy"
    ],
    "crime and punishment": [
        "crime", "criminal", "arrest", "prison", "sentence", "murder", "theft",
        "violence", "police", "conviction", "penalty", "jail", "guilty", "shooting",
        "stabbing", "robbery", "fraud", "corruption", "bribery", "trafficking",
        "drug", "gang", "weapon", "assault", "rape", "kidnapping", "terrorism",
        "extremism", "radicalization", "bomb", "explosion", "hostage", "ransom",
        "homicide", "manslaughter", "arson", "vandalism", "cybercrime", "hacking",
        "smuggling", "money laundering", "suspect", "fugitive", "investigation",
        "detective", "fbi", "interpol", "warrant", "raid", "crackdown", "enforcement"
    ],
    "security and defense": [
        "security", "military", "war", "defense", "threat", "attack", "weapon",
        "soldier", "terrorism", "conflict", "army", "nato", "missile", "nuclear",
        "intelligence", "spy", "surveillance", "border", "patrol", "guard",
        "navy", "air force", "marines", "special forces", "combat", "battlefield",
        "ceasefire", "peace talks", "sanctions", "embargo", "blockade", "invasion",
        "occupation", "resistance", "insurgency", "drone", "airstrike", "casualties",
        "civilian", "refugee", "displacement", "war crime", "genocide", "ethnic cleansing",
        "cybersecurity", "cyberattack", "espionage", "counterterrorism", "homeland"
    ],
    "health and safety": [
        "health", "disease", "medical", "hospital", "patient", "vaccine", "treatment",
        "safety", "mental health", "epidemic", "cancer", "doctor", "nurse", "surgery",
        "medication", "drug", "pharmaceutical", "clinical", "diagnosis", "symptom",
        "infection", "virus", "bacteria", "pandemic", "outbreak", "quarantine",
        "lockdown", "public health", "healthcare", "insurance", "therapy", "counseling",
        "psychiatry", "psychology", "wellbeing", "nutrition", "diet", "exercise",
        "obesity", "diabetes", "heart disease", "alzheimer", "depression", "anxiety",
        "suicide", "addiction", "rehabilitation", "emergency", "ambulance", "icu"
    ],
    "quality of life": [
        "quality", "living", "welfare", "community", "happiness", "lifestyle",
        "housing", "poverty", "standard", "wellbeing", "comfort", "satisfaction",
        "leisure", "recreation", "entertainment", "sport", "arts", "culture",
        "education", "literacy", "opportunity", "mobility", "social", "neighborhood",
        "urban", "rural", "suburban", "development", "progress", "modernization",
        "clean", "environment", "pollution", "green", "sustainable", "biodiversity",
        "parks", "public space", "transportation", "commute", "traffic", "noise",
        "crime rate", "safety", "community services", "social services", "support"
    ],
    "cultural identity": [
        "culture", "identity", "tradition", "heritage", "nationality", "ethnic",
        "religion", "language", "community", "custom", "immigrant", "migration",
        "diaspora", "indigenous", "native", "aboriginal", "assimilation", "integration",
        "multiculturalism", "nationalism", "patriotism", "flag", "anthem", "symbol",
        "history", "historical", "colonial", "postcolonial", "slavery", "reparation",
        "monument", "statue", "museum", "art", "literature", "music", "film",
        "food", "cuisine", "fashion", "festival", "celebration", "holiday",
        "generational", "values", "norms", "social norms", "taboo", "stereotype"
    ],
    "public opinion": [
        "opinion", "poll", "survey", "public", "sentiment", "popularity", "approval",
        "support", "protest", "movement", "demand", "petition", "referendum",
        "election", "voters", "citizens", "community", "grassroots", "campaign",
        "social media", "twitter", "facebook", "trending", "viral", "backlash",
        "criticism", "praise", "controversy", "debate", "discussion", "conversation",
        "perception", "attitude", "belief", "trust", "confidence", "satisfaction",
        "dissatisfaction", "anger", "frustration", "hope", "fear", "concern",
        "awareness", "advocacy", "lobbying", "pressure group", "think tank"
    ],
    "political": [
        "political", "election", "party", "democrat", "republican", "parliament",
        "vote", "politician", "government", "president", "congress", "senate",
        "prime minister", "cabinet", "minister", "opposition", "coalition",
        "campaign", "ballot", "polling", "candidate", "incumbent", "term",
        "administration", "white house", "downing street", "kremlin", "beijing",
        "left wing", "right wing", "liberal", "conservative", "progressive",
        "populist", "nationalist", "socialist", "communist", "capitalist",
        "geopolitical", "diplomacy", "foreign affairs", "summit", "bilateral",
        "multilateral", "un", "eu", "nato", "g7", "g20", "imf", "world bank"
    ],
    "external regulation and reputation": [
        "international", "global", "foreign", "diplomacy", "sanction", "reputation",
        "alliance", "treaty", "united nations", "trade deal", "bilateral", "multilateral",
        "world trade", "wto", "imf", "world bank", "eu", "nato", "asean", "g20",
        "soft power", "hard power", "influence", "credibility", "image", "brand",
        "ranking", "index", "rating", "assessment", "report card", "accountability",
        "transparency", "corruption index", "press freedom", "human rights report",
        "trade relations", "diplomatic ties", "embassy", "consul", "ambassador",
        "visa", "passport", "border control", "immigration policy", "asylum"
    ],
    "other": []
}
def score_frames(text):
    text_lower = text.lower()
    scores = {}
    total = 0

    for frame, keywords in FRAME_KEYWORDS.items():
        if frame == "other":
            continue
        count = sum(text_lower.count(kw) for kw in keywords)
        scores[frame] = count
        total += count

    # Normalize scores
    if total > 0:
        for frame in scores:
            scores[frame] = round(scores[frame] / total, 4)
    else:
        for frame in scores:
            scores[frame] = 0.0

    # "other" gets whatever is left
    scores["other"] = round(max(0, 1 - sum(scores.values())), 4)
    return scores

def save_frames(article_id, scores):
    conn = get_db_connection()
    cursor = conn.cursor()
    dominant = max(scores, key=scores.get)

    for frame, score in scores.items():
        cursor.execute("""
            INSERT INTO article_frames (article_id, frame_label, score, is_dominant)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (article_id, frame_label) DO UPDATE SET score = EXCLUDED.score
        """, (article_id, frame, score, frame == dominant))

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

print(f"Analyzing {len(articles)} articles...")

for i, (article_id, title, description, content) in enumerate(articles):
    text = f"{title} {description or ''} {content or ''}"
    scores = score_frames(text)
    save_frames(article_id, scores)
    dominant = max(scores, key=scores.get)
    print(f"{i+1}/{len(articles)} | {title[:50]}")
    print(f"         Dominant: {dominant} ({scores[dominant]})")

print("\nDone!")