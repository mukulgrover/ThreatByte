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
NVIDIA_DEFAULT_MODEL = "meta/llama-3.1-8b-instruct"
NVIDIA_FALLBACK_MODEL = "meta/llama-3.1-70b-instruct"

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
CTI_SYSTEM_PROMPT = """You are a senior cybersecurity editor and threat intelligence analyst for ThreatByte.
Your task is to analyze breaking cybersecurity news from the last 24 hours and produce a realistic, deeply informative, human-readable intelligence briefing in structured JSON.

Write in a clear, authoritative editorial tone (similar to The Record by Recorded Future or BleepingComputer). Avoid cheesy hype words or robotic filler phrases. Focus on real-world operational risk, technical facts, CVEs, affected software versions, and concrete mitigations.

Output strictly valid JSON matching this schema:
{
  "title": "Clear, informative headline describing the core incident or vulnerability",
  "threat_category": "One of: Ransomware | Data Breach | 0-Day & Exploit | Nation-State/APT | Cloud & Supply Chain | Vulnerability / Advisory",
  "severity": "One of: CRITICAL | HIGH | MEDIUM | LOW",
  "severity_score": float between 1.0 and 10.0,
  "target_sectors": ["Enterprise", "Healthcare", "Finance", etc.],
  "affected_vendors": ["Microsoft", "Cisco", "Fortinet", etc.],
  "cve_ids": ["CVE-2026-XXXX"],
  "threat_actor": "Name of threat group (or 'Unknown / Unattributed')",
  "executive_summary": "2-3 well-written sentences summarizing the attack, scope of impact, and immediate risk for security teams.",
  "technical_breakdown": "3-4 concise sentences detailing the attack vector, root cause, privilege level required, and exploitation mechanics.",
  "actionable_mitigations": [
    "Specific patching guidance or vendor version to upgrade to",
    "Network containment, firewall, or port isolation recommendations",
    "Detection indicators (EDR, log query, or Sigma/YARA pointers)"
  ],
  "telegram_snippet": "A concise 2-sentence summary with essential context suitable for a rapid morning Telegram bulletin."
}

CRITICAL:
- Output ONLY the raw JSON object. Do not include markdown code fences (```json).
- Be technically accurate.
"""
