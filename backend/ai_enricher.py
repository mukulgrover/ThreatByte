"""
AI Threat Intelligence Reasoning & Enrichment Engine using NVIDIA NIM API.
"""
import json
import sys
import re
from pathlib import Path
from typing import Dict, Any, Optional
import requests

# Ensure repository root is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.config import (
    NVIDIA_API_KEY,
    NVIDIA_BASE_URL,
    NVIDIA_DEFAULT_MODEL,
    NVIDIA_FALLBACK_MODEL,
    CTI_SYSTEM_PROMPT
)

def clean_json_text(text: str) -> str:
    """Strip markdown backticks or preambles from LLM JSON response."""
    text = text.strip()
    # Remove markdown ```json ... ``` or ``` ... ```
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    text = text.strip()
    return text

def extract_cves_heuristic(text: str) -> list:
    """Extract CVE-YYYY-NNNNN patterns from text."""
    matches = re.findall(r"CVE-\d{4}-\d{4,7}", text, re.IGNORECASE)
    return list(set([m.upper() for m in matches]))

def fallback_heuristic_enrichment(raw_article: Dict[str, Any]) -> Dict[str, Any]:
    """
    Intelligent local heuristic fallback when NVIDIA API key is not configured
    or during local offline development/testing.
    """
    title = raw_article.get("title", "")
    content = raw_article.get("content", "")
    source = raw_article.get("source", "")
    url = raw_article.get("url", "")
    published_at = raw_article.get("published_at", "")
    combined_text = f"{title} {content}"

    cves = extract_cves_heuristic(combined_text)
    
    # Determine category & severity based on threat keywords
    lower_text = combined_text.lower()
    
    if any(k in lower_text for k in ["zero-day", "0-day", "actively exploited", "unauthenticated rce", "critical cve"]):
        category = "0-Day & Exploit"
        severity = "CRITICAL"
        score = 9.5
    elif any(k in lower_text for k in ["ransomware", "encryptor", "lockbit", "blackcat", "extortion", "ransom"]):
        category = "Ransomware"
        severity = "HIGH"
        score = 8.8
    elif any(k in lower_text for k in ["data breach", "leaked", "records exposed", "hacked database", "breached"]):
        category = "Data Breach"
        severity = "HIGH"
        score = 8.2
    elif any(k in lower_text for k in ["apt", "nation-state", "espionage", "russian", "chinese", "iranian", "north korean"]):
        category = "Nation-State/APT"
        severity = "HIGH"
        score = 8.5
    elif any(k in lower_text for k in ["cloud", "aws", "azure", "kubernetes", "supply chain", "npm", "pypi"]):
        category = "Cloud & Supply Chain"
        severity = "MEDIUM"
        score = 7.2
    else:
        category = "Vulnerability / Advisory"
        severity = "MEDIUM"
        score = 6.5

    # Extract target vendors
    vendors = []
    known_vendors = ["Microsoft", "Google", "Apple", "Cisco", "Fortinet", "Ivanti", "Palo Alto", "CrowdStrike", "AWS", "VMware", "Linux", "Apache", "Citrix", "SAP"]
    for v in known_vendors:
        if re.search(rf"\b{v}\b", combined_text, re.IGNORECASE):
            vendors.append(v)

    # Executive summary
    first_sentence = content.split(". ")[0] if ". " in content else content[:150]
    exec_summary = f"{title}. {first_sentence}." if first_sentence else title

    return {
        "title": title,
        "source": source,
        "url": url,
        "published_at": published_at,
        "threat_category": category,
        "severity": severity,
        "severity_score": score,
        "target_sectors": ["Enterprise", "Critical Infrastructure"],
        "affected_vendors": vendors if vendors else ["General Industry"],
        "cve_ids": cves,
        "threat_actor": "Unknown / Under Investigation",
        "executive_summary": exec_summary,
        "technical_breakdown": f"Analysis of incident reported by {source}. The threat involves attack vectors targeting {', '.join(vendors) if vendors else 'standard services'}. Further technical telemetry is developing.",
        "actionable_mitigations": [
            "Review firewall and perimeter access logs for anomalous traffic patterns.",
            "Verify all endpoint detection (EDR) agents are updated with latest behavioral signatures.",
            "Audit exposed external assets and apply vendor security patches immediately."
        ],
        "telegram_snippet": f"🚨 *{severity} Threat*: {title} — Impacting {', '.join(vendors) if vendors else 'systems'}. Immediate patching and log auditing recommended."
    }

def analyze_with_nvidia_nim(raw_article: Dict[str, Any], model: str = NVIDIA_DEFAULT_MODEL) -> Optional[Dict[str, Any]]:
    """
    Call NVIDIA NIM API to reason through the cyber incident and produce
    a rich structured intelligence dossier.
    """
    if not NVIDIA_API_KEY:
        return None

    content_snippet = (raw_article.get('content') or '')[:500]
    user_prompt = f"SOURCE: {raw_article.get('source')}\nHEADLINE: {raw_article.get('title')}\nCONTENT: {content_snippet}"

    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": CTI_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 500
    }

    try:
        url = f"{NVIDIA_BASE_URL}/chat/completions"
        resp = requests.post(url, headers=headers, json=payload, timeout=12)
        
        if resp.status_code == 200:
            data = resp.json()
            raw_content = data["choices"][0]["message"]["content"]
            cleaned = clean_json_text(raw_content)
            
            # Extract JSON object from output if surrounded by text
            json_match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
            if json_match:
                cleaned = json_match.group(1)

            parsed = json.loads(cleaned)
            
            # Attach metadata
            parsed["source"] = raw_article.get("source")
            parsed["url"] = raw_article.get("url")
            parsed["published_at"] = raw_article.get("published_at")
            
            # Ensure CVEs list is populated if missing in LLM response
            if not parsed.get("cve_ids"):
                parsed["cve_ids"] = extract_cves_heuristic(raw_article.get("title", "") + " " + raw_article.get("content", ""))
                
            return parsed
        else:
            print(f"[!] NVIDIA NIM API returned status {resp.status_code}", flush=True)

    except Exception as e:
        print(f"[!] NVIDIA NIM inference error / timeout: {e}", flush=True)

    return None

def enrich_article(raw_article: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enriches a raw article using NVIDIA NIM LLM, falling back to local heuristic reasoning
    if API key is not present or an API issue occurs.
    """
    if NVIDIA_API_KEY:
        print(f"    [*] Reasoning with NVIDIA NIM for: {raw_article.get('title')[:60]}...", flush=True)
        enriched = analyze_with_nvidia_nim(raw_article)
        if enriched:
            return enriched
        print("    [!] Falling back to local heuristic enrichment...", flush=True)

    return fallback_heuristic_enrichment(raw_article)
