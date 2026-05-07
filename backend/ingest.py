"""
ZeroHour - Data ingestion module.

Supports:
  - Mock tweet injection (guaranteed demo data).
  - snscrape scraper (real Twitter data, no API key needed).
"""

import uuid
import random
from datetime import datetime, timedelta
from backend.database import insert_tweet
from backend.sentiment import analyze

# ── Mock data ────────────────────────────────────────────────────────────────

MOCK_TWEETS = [
    # CRITICAL
    ("@user1", "BREAKING: Explosion reported near the central station. Multiple casualties feared. Authorities on scene. #urgent", "Mumbai"),
    ("@reporter99", "Eyewitness: loud blast heard in downtown, buildings shaking, people running. This is terrifying. #breaking", "Delhi"),
    ("@newsflash", "Mass evacuation ordered after chemical plant fire causes toxic cloud. Residents told to stay indoors immediately.", "Pune"),
    # HIGH
    ("@citywatch", "Major flooding in low-lying areas after dam overflow. Rescue teams deployed. Road closures in effect.", "Chennai"),
    ("@safetyalert", "Wildfire spreading rapidly near residential area. Firefighters battling heavy winds. Evacuation in progress.", "Bengaluru"),
    ("@localreport", "Violent clashes reported at protest. Police used tear gas. Several injured and hospitalised.", "Hyderabad"),
    ("@emergencyRT", "Earthquake tremors felt across city. Magnitude 5.2 recorded. People evacuating buildings.", "Kolkata"),
    # MEDIUM
    ("@trafficupd8", "Major accident on highway 48, 3 vehicles involved. Traffic backed up 10km. Emergency services present.", "Jaipur"),
    ("@watchdog", "Suspicious package found near parliament building. Bomb squad called. Area cordoned off.", "Delhi"),
    ("@citydesk", "Protest turning heated outside city hall. Large crowd gathering, police on standby.", "Mumbai"),
    # LOW / NEUTRAL
    ("@normalguy", "Heavy rain today but roads are fine. Take care everyone 🌧️", "Bengaluru"),
    ("@weatherbot", "Moderate winds expected this evening. No major disruptions anticipated.", "Chennai"),
    ("@citizen42", "Power outage in sector 7 since morning. Awaiting electricity board response.", "Noida"),
    ("@localgovt", "Scheduled road maintenance tomorrow. Minor diversions expected on MG Road.", "Bengaluru"),
]


def _make_mock_tweet(username: str, content: str, location: str, offset_minutes: int = 0) -> dict:
    ts = (datetime.utcnow() - timedelta(minutes=offset_minutes)).strftime("%Y-%m-%dT%H:%M:%S")
    analysis = analyze(content)
    keywords = ",".join(content.lower().split()[:5])
    return {
        "tweet_id": str(uuid.uuid4()),
        "username": username,
        "content": content,
        "created_at": ts,
        "source": "mock",
        "location": location,
        "keywords": keywords,
        "raw_vader": analysis["raw_vader"],
        "llm_label": analysis["llm_label"],
        "llm_score": analysis["llm_score"],
        "authority": 0,
    }


def seed_mock_data(n: int = None) -> int:
    """Inject mock tweets into the database. Returns number inserted."""
    tweets = MOCK_TWEETS if n is None else MOCK_TWEETS[:n]
    inserted = 0
    for i, (user, content, loc) in enumerate(tweets):
        offset = random.randint(0, 90)  # spread over last 90 mins
        tweet = _make_mock_tweet(user, content, loc, offset)
        row_id = insert_tweet(tweet)
        if row_id:
            inserted += 1
    return inserted


# ── snscrape wrapper ──────────────────────────────────────────────────────────

def scrape_twitter(query: str, limit: int = 50) -> int:
    """
    Scrape tweets using snscrape and persist them.
    Falls back silently if snscrape is not installed or network fails.
    Returns number of tweets inserted.
    """
    try:
        import snscrape.modules.twitter as sntwitter  # type: ignore
    except ImportError:
        print("[Scraper] snscrape not installed — skipping live scrape.")
        return 0

    inserted = 0
    try:
        scraper = sntwitter.TwitterSearchScraper(query)
        for i, tweet in enumerate(scraper.get_items()):
            if i >= limit:
                break
            content = tweet.rawContent or tweet.content or ""
            analysis = analyze(content)
            data = {
                "tweet_id": str(tweet.id),
                "username": f"@{tweet.user.username}",
                "content": content,
                "created_at": tweet.date.strftime("%Y-%m-%dT%H:%M:%S"),
                "source": "snscrape",
                "location": tweet.place.fullName if tweet.place else "",
                "keywords": query,
                "raw_vader": analysis["raw_vader"],
                "llm_label": analysis["llm_label"],
                "llm_score": analysis["llm_score"],
                "authority": 0,
            }
            if insert_tweet(data):
                inserted += 1
    except Exception as exc:
        print(f"[Scraper] snscrape error — {exc}")

    return inserted
