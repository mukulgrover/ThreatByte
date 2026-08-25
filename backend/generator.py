"""
Master Orchestration Script for CyberPulse Threat Intelligence Pipeline.
"""
import sys
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

# Ensure repository root is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.config import DATA_DIR, DAILY_DIR
from backend.scraper import collect_daily_intelligence
from backend.ai_enricher import enrich_article
from backend.telegram_bot import broadcast_daily_briefing

def calculate_daily_metrics(articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate summary threat statistics for the daily executive dashboard."""
    total = len(articles)
    critical_count = sum(1 for a in articles if a.get("severity", "").upper() == "CRITICAL")
    high_count = sum(1 for a in articles if a.get("severity", "").upper() == "HIGH")
    medium_count = sum(1 for a in articles if a.get("severity", "").upper() == "MEDIUM")
    low_count = sum(1 for a in articles if a.get("severity", "").upper() == "LOW")
    
    # Collect all unique CVEs
    all_cves = set()
    for a in articles:
        for cve in a.get("cve_ids", []):
            if cve:
                all_cves.add(cve)

    # Collect top affected vendors
    vendor_freq = {}
    for a in articles:
        for v in a.get("affected_vendors", []):
            if v and v not in ["General Industry", "None", "Unknown"]:
                vendor_freq[v] = vendor_freq.get(v, 0) + 1
                
    top_vendors = sorted(vendor_freq.items(), key=lambda x: x[1], reverse=True)[:5]
    top_vendors_list = [v[0] for v in top_vendors]

    # Global Threat Level Calculation
    if critical_count >= 2 or len(all_cves) >= 3:
        threat_level = "ELEVATED (LEVEL ORANGE)"
        threat_badge = "CRITICAL RISK"
    elif critical_count >= 1 or high_count >= 3:
        threat_level = "GUARDED (LEVEL YELLOW)"
        threat_badge = "HIGH SURGE"
    else:
        threat_level = "NOMINAL (LEVEL BLUE)"
        threat_badge = "MODERATE"

    return {
        "total_incidents": total,
        "critical_threats": critical_count,
        "high_threats": high_count,
        "medium_threats": medium_count,
        "low_threats": low_count,
        "unique_cves_count": len(all_cves),
        "unique_cves": sorted(list(all_cves)),
        "top_affected_vendors": top_vendors_list,
        "overall_threat_level": threat_level,
        "threat_badge": threat_badge
    }

def update_archive_registry(date_str: str, metrics: Dict[str, Any], top_headline: str):
    """Maintain historical index of all past briefings in data/archive.json."""
    archive_file = DATA_DIR / "archive.json"
    archive_data = []

    if archive_file.exists():
        try:
            with open(archive_file, "r", encoding="utf-8") as f:
                archive_data = json.load(f)
        except Exception as e:
            print(f"[!] Warning: Could not read existing archive.json: {e}")
            archive_data = []

    # Remove existing entry for same date if re-running
    archive_data = [item for item in archive_data if item.get("date") != date_str]

    # Insert new entry at the beginning
    archive_data.insert(0, {
        "date": date_str,
        "top_headline": top_headline,
        "total_incidents": metrics["total_incidents"],
        "critical_threats": metrics["critical_threats"],
        "overall_threat_level": metrics["overall_threat_level"]
    })

    with open(archive_file, "w", encoding="utf-8") as f:
        json.dump(archive_data, f, indent=2)

    print(f"[+] Updated historical archive registry ({len(archive_data)} days archived).")

def run_daily_pipeline(mock_mode: bool = False):
    """
    Execute full CTI aggregation, AI reasoning, datastore persistence,
    and Telegram broadcast.
    """
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S UTC")

    print("\n" + "="*60, flush=True)
    print(f"🛡️  THREATBYTE CTI PIPELINE STARTING | {timestamp_str}", flush=True)
    print("="*60, flush=True)

    # 1. Ingestion
    raw_articles = collect_daily_intelligence(max_age_hours=36)
    if not raw_articles:
        print("[!] No recent articles found from CTI feeds.", flush=True)
        return

    # 2. AI Reasoning & Enrichment
    enriched_articles = []
    print(f"\n[*] Enriching {len(raw_articles)} threat intelligence items with AI reasoning...", flush=True)
    for idx, raw in enumerate(raw_articles, 1):
        print(f"[{idx}/{len(raw_articles)}] Processing: {raw.get('title')[:60]}...", flush=True)
        enriched = enrich_article(raw)
        enriched_articles.append(enriched)

    # Sort enriched articles: CRITICAL first, then HIGH, then MEDIUM, then LOW
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    enriched_articles.sort(key=lambda x: severity_order.get(x.get("severity", "MEDIUM").upper(), 2))

    # 3. Calculate Executive Metrics
    metrics = calculate_daily_metrics(enriched_articles)
    top_headline = enriched_articles[0].get("title", "Cyber Threat Intelligence Briefing") if enriched_articles else "Daily Briefing"

    payload = {
        "date": date_str,
        "generated_at": timestamp_str,
        "metrics": metrics,
        "articles": enriched_articles
    }

    # 4. Save to JSON files
    daily_file = DAILY_DIR / f"{date_str}.json"
    latest_file = DATA_DIR / "latest.json"

    with open(daily_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"[+] Saved daily payload to {daily_file}", flush=True)

    with open(latest_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"[+] Updated latest payload at {latest_file}", flush=True)

    # 5. Update Historical Archive Index
    update_archive_registry(date_str, metrics, top_headline)

    # 6. Broadcast to Telegram Subscribers
    print("\n[*] Preparing Telegram Subscriber Broadcast...", flush=True)
    broadcast_daily_briefing(enriched_articles, date_str)

    print("\n" + "="*60, flush=True)
    print(f"✅ THREATBYTE DAILY PIPELINE COMPLETED SUCCESSFULLY!", flush=True)
    print(f"📊 Summary: {metrics['total_incidents']} Incidents | {metrics['critical_threats']} Critical | {metrics['unique_cves_count']} CVEs", flush=True)
    print("="*60 + "\n", flush=True)

if __name__ == "__main__":
    run_daily_pipeline()
