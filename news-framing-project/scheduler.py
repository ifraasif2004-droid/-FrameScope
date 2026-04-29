import schedule
import time
import subprocess
import sys

def run_pipeline():
    print("\n🔄 Running news pipeline...")
    
    # Step 1: Fetch new articles from Guardian
    print("📰 Fetching new articles...")
    subprocess.run([sys.executable, "fetch_guardian.py"])
    
    # Step 2: Scrape full text for new articles
    print("🔍 Scraping full text...")
    subprocess.run([sys.executable, "scrape_fulltext.py"])
    
    # Step 3: Run frame analysis on new articles
    print("🧠 Analyzing frames...")
    subprocess.run([sys.executable, "analyze_frames.py"])
    
    # Step 4: Run tone analysis
    print("🎭 Analyzing tone...")
    subprocess.run([sys.executable, "tone_analysis.py"])
    
    # Step 5: Assign countries
    print("🌍 Assigning countries...")
    subprocess.run([sys.executable, "assign_countries.py"])
    
    print("✅ Pipeline complete!")

# Run immediately on start
run_pipeline()

# Then run every 1 hours automatically
schedule.every(1).hours.do(run_pipeline)    # every hour

print("⏰ Scheduler running — fetching new articles every 6 hours")
print("Press Ctrl+C to stop")

while True:
    schedule.run_pending()
    time.sleep(60)