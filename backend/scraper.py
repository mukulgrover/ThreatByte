"""
Scraper and deduplication module for Cyber Threat Intelligence feeds.
"""
import re
import sys
import html
import time
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
import requests
import feedparser
from bs4 import BeautifulSoup

# Ensure repository root is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.config import RSS_FEEDS, MAX_ITEMS_TO_ANALYZE

def clean_html_text(raw_html: str) -> str:
    """Strip HTML tags and unescape entities to return clean text."""
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    # Remove script and style elements
    for script_or_style in soup(["script", "style", "noscript"]):
        script_or_style.extract()
    text = soup.get_text(separator=" ", strip=True)
    # Unescape HTML entities and collapse whitespace
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def parse_published_time(entry: Any) -> datetime:
    """Parse publication time from an RSS entry with multiple fallbacks."""
    now = datetime.now(timezone.utc)
    
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            return datetime.fromtimestamp(time.mktime(entry.published_parsed), tz=timezone.utc)
        except Exception:
            pass
            
    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        try:
            return datetime.fromtimestamp(time.mktime(entry.updated_parsed), tz=timezone.utc)
        except Exception:
            pass

    return now

def normalize_title(title: str) -> str:
    """Normalize headline string for similarity deduplication."""
    clean = re.sub(r"[^\w\s]", "", title.lower())
    words = clean.split()
    # Return sorted key words longer than 3 letters
    return " ".join(sorted([w for w in words if len(w) > 3]))

def fetch_feed_articles(feed_info: Dict[str, str], max_age_hours: int = 36) -> List[Dict[str, Any]]:
    """Fetch and parse articles from a single RSS feed."""
    articles = []
    feed_url = feed_info["url"]
    source_name = feed_info["name"]
    category_hint = feed_info["category"]

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 CyberPulse/1.0"
        }
        resp = requests.get(feed_url, headers=headers, timeout=12)
        if resp.status_code != 200:
            print(f"[!] Warning: Feed {source_name} returned HTTP {resp.status_code}")
            return []

        parsed = feedparser.parse(resp.content)
        now = datetime.now(timezone.utc)
        time_cutoff = now - timedelta(hours=max_age_hours)

        for entry in parsed.entries:
            pub_date = parse_published_time(entry)
            
            # Filter by time window (last max_age_hours)
            if pub_date < time_cutoff:
                continue

            raw_title = getattr(entry, "title", "Untitled")
            clean_title = clean_html_text(raw_title)
            link = getattr(entry, "link", "")
            
            # Extract content / summary
            summary = ""
            if hasattr(entry, "summary"):
                summary = entry.summary
            elif hasattr(entry, "content") and entry.content:
                summary = entry.content[0].value
            elif hasattr(entry, "description"):
                summary = entry.description
                
            clean_content = clean_html_text(summary)
            
            # Skip empty or trivially short items
            if not clean_title or len(clean_content) < 30:
                continue

            articles.append({
                "source": source_name,
                "category_hint": category_hint,
                "title": clean_title,
                "url": link,
                "published_at": pub_date.isoformat(),
                "content": clean_content[:2000],  # Keep reasonable context for LLM
                "normalized_key": normalize_title(clean_title)
            })

    except Exception as e:
        print(f"[!] Error fetching feed {source_name} ({feed_url}): {e}")

    return articles

def deduplicate_articles(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deduplicate articles using word token overlap."""
    unique_articles = []
    seen_keys = []

    for art in articles:
        current_words = set(art["normalized_key"].split())
        if not current_words:
            unique_articles.append(art)
            continue

        is_duplicate = False
        for seen in seen_keys:
            # Check Jaccard similarity between title word sets
            overlap = len(current_words.intersection(seen))
            total = len(current_words.union(seen))
            if total > 0 and (overlap / total) > 0.55:
                is_duplicate = True
                break

        if not is_duplicate:
            seen_keys.append(current_words)
            unique_articles.append(art)

    return unique_articles

def collect_daily_intelligence(max_age_hours: int = 36) -> List[Dict[str, Any]]:
    """
    Main ingestion function. Pulls from all configured RSS feeds,
    deduplicates, sorts chronologically, and limits to top items.
    """
    all_articles = []
    print(f"[*] Aggregating CTI feeds from {len(RSS_FEEDS)} industry sources...")
    
    for feed in RSS_FEEDS:
        print(f"    -> Fetching {feed['name']}...")
        feed_articles = fetch_feed_articles(feed, max_age_hours=max_age_hours)
        all_articles.extend(feed_articles)
        print(f"       Got {len(feed_articles)} recent items.")

    print(f"[*] Total raw articles fetched: {len(all_articles)}")
    
    # If feeds didn't return recent items (e.g. strict time window on slow news morning), expand window
    if len(all_articles) < 3:
        print("[!] Low article count, expanding time window to 72 hours...")
        for feed in RSS_FEEDS:
            feed_articles = fetch_feed_articles(feed, max_age_hours=72)
            all_articles.extend(feed_articles)

    deduped = deduplicate_articles(all_articles)
    print(f"[*] Unique articles after deduplication: {len(deduped)}")

    # Sort descending by published_at
    deduped.sort(key=lambda x: x["published_at"], reverse=True)

    # Return top N items for AI analysis
    selected = deduped[:MAX_ITEMS_TO_ANALYZE]
    return selected

if __name__ == "__main__":
    items = collect_daily_intelligence()
    print(f"\n[+] Fetched {len(items)} top articles:")
    for idx, item in enumerate(items, 1):
        print(f"{idx}. [{item['source']}] {item['title']} ({item['url']})")
