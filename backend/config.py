"""
Configuration module for ThreatByte Threat Intelligence Aggregator & Analyzer.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure root dir is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Ensure UTF-8 stdout on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Load environment variables from .env if present
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DAILY_DIR = DATA_DIR / "daily"
FRONTEND_DIR = BASE_DIR / "frontend"
SUBSCRIBERS_FILE = DATA_DIR / "subscribers.json"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
DAILY_DIR.mkdir(parents=True, exist_ok=True)

# API Keys & Secrets
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "").strip()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
TELEGRAM_BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME", "threatbytebot").strip().lstrip("@")
SITE_URL = os.getenv("SITE_URL", "https://mukulgrover.github.io/ThreatByte").rstrip("/")

# NVIDIA NIM LLM Configuration
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
NVIDIA_DEFAULT_MODEL = "meta/llama-3.2-11b-vision-instruct"
NVIDIA_FALLBACK_MODEL = "meta/llama-3.2-11b-vision-instruct"

# Maximum items to analyze per run
MAX_ITEMS_TO_ANALYZE = 10
TOP_STORIES_FOR_TELEGRAM = 5

# Curated High-Fidelity Cybersecurity News & CTI Feeds
RSS_FEEDS = [
    {
        "name": "BleepingComputer",
        "url": "https://www.bleepingcomputer.com/feed/",
        "category": "Ransomware & Exploits"
    },
    {
        "name": "The Hacker News",
        "url": "https://feeds.feedburner.com/TheHackersNews",
        "category": "Vulnerabilities & 0-Days"
    },
    {
        "name": "Krebs on Security",
        "url": "https://krebsonsecurity.com/feed/",
        "category": "Data Leaks & Cybercrime"
    },
    {
        "name": "Dark Reading",
        "url": "https://www.darkreading.com/rss.xml",
        "category": "Threat Intelligence"
    },
    {
        "name": "SecurityWeek",
        "url": "https://www.securityweek.com/feed/",
        "category": "Enterprise Security & Breaches"
    },
    {
        "name": "SANS Internet Storm Center",
        "url": "https://isc.sans.edu/rssfeed.xml",
        "category": "Incident Handling"
    }
]

# AI Threat Analyst Prompt
CTI_SYSTEM_PROMPT = """You are a senior cybersecurity threat intelligence analyst for ThreatByte.
Analyze the provided cybersecurity news and return ONLY a valid JSON object matching this schema:
{
  "title": "Clear informative headline describing the incident",
  "threat_category": "Ransomware | Data Breach | 0-Day & Exploit | Nation-State/APT | Cloud & Supply Chain | Vulnerability / Advisory",
  "severity": "CRITICAL | HIGH | MEDIUM | LOW",
  "severity_score": 8.5,
  "target_sectors": ["Enterprise", "Government"],
  "affected_vendors": ["Vendor Name"],
  "cve_ids": ["CVE-2026-XXXX"],
  "threat_actor": "Actor name or 'Unknown / Unattributed'",
  "executive_summary": "2 concise sentences summarizing attack vector, impact and operational risk.",
  "technical_breakdown": "2 concise sentences detailing exploitation mechanics and root cause.",
  "actionable_mitigations": [
    "Specific patching or software upgrade guidance",
    "Network containment or firewall rules",
    "Detection and log monitoring indicators"
  ],
  "telegram_snippet": "A concise 2-sentence summary suitable for a rapid morning Telegram bulletin."
}
Return raw JSON only with NO markdown fences."""
