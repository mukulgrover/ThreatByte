"""
Telegram Subscriber & Broadcasting Module for ThreatByte.
Handles automated subscriber registration, welcome messages, and morning intelligence broadcasts.
"""
import sys
import json
import html
from pathlib import Path
from typing import List, Dict, Any, Set
import requests

# Ensure repository root is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    TELEGRAM_BOT_USERNAME,
    SITE_URL,
    TOP_STORIES_FOR_TELEGRAM,
    SUBSCRIBERS_FILE,
    DATA_DIR
)

def escape_html(text: str) -> str:
    """Escape special HTML characters for Telegram HTML mode."""
    if not text:
        return ""
    return html.escape(str(text))

def load_subscribers() -> List[Dict[str, Any]]:
    """Load list of registered Telegram chat IDs from data/subscribers.json."""
    if not SUBSCRIBERS_FILE.exists():
        return []
    try:
        with open(SUBSCRIBERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[!] Error loading subscribers.json: {e}")
        return []

def save_subscribers(subscribers: List[Dict[str, Any]]):
    """Save subscribers list to data/subscribers.json."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(SUBSCRIBERS_FILE, "w", encoding="utf-8") as f:
        json.dump(subscribers, f, indent=2)

def register_subscriber(chat_id: int | str, user_info: Dict[str, Any] = None) -> bool:
    """Register a new user or channel chat_id for daily broadcasts."""
    chat_id_str = str(chat_id)
    subscribers = load_subscribers()
    
    existing = next((s for s in subscribers if str(s.get("chat_id")) == chat_id_str), None)
    if existing:
        return False  # Already registered

    info = {
        "chat_id": chat_id_str,
        "first_name": (user_info or {}).get("first_name", "Anonymous"),
        "username": (user_info or {}).get("username", ""),
        "subscribed_at": user_info.get("date", "") if user_info else "",
        "active": True
    }
    subscribers.append(info)
    save_subscribers(subscribers)
    print(f"[+] New ThreatByte subscriber registered: {info['first_name']} (@{info['username']}, ID: {chat_id_str})")
    return True

def sync_telegram_subscribers() -> int:
    """
    Fetch recent updates from Telegram Bot API to register anyone who clicked /start
    or messaged the bot, and send them a welcome confirmation.
    """
    if not TELEGRAM_BOT_TOKEN:
        return 0

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    new_subs_count = 0

    try:
        resp = requests.get(url, timeout=12)
        if resp.status_code != 200:
            return 0

        updates = resp.json().get("result", [])
        for u in updates:
            msg = u.get("message") or u.get("channel_post") or u.get("my_chat_member")
            if not msg:
                continue

            chat = msg.get("chat", {})
            chat_id = chat.get("id")
            from_user = msg.get("from", {})
            text = (msg.get("text") or "").strip()

            if chat_id:
                is_new = register_subscriber(chat_id, {
                    "first_name": from_user.get("first_name") or chat.get("title") or "Subscriber",
                    "username": from_user.get("username") or chat.get("username") or "",
                    "date": str(msg.get("date", ""))
                })
                
                if is_new or text in ["/start", "/subscribe", "/help"]:
                    send_welcome_message(chat_id)
                    if is_new:
                        new_subs_count += 1

    except Exception as e:
        print(f"[!] Error syncing Telegram subscribers: {e}")

    return new_subs_count

def send_welcome_message(chat_id: str | int):
    """Send an onboarding welcome message to a newly registered user."""
    welcome_text = (
        "🛡️ <b>Welcome to ThreatByte Daily Intelligence!</b>\n\n"
        "You are now subscribed to automated morning cybersecurity bulletins.\n\n"
        "<b>What you will receive every morning:</b>\n"
        "• Curated 24h analysis of breaking data breaches, 0-days & ransomware.\n"
        "• Severity ratings, affected software versions & CVE tags.\n"
        "• Direct links to our web dashboard for full technical deep-dives.\n\n"
        f"🌐 <b>Web Dashboard:</b> <a href=\"{SITE_URL}\">Open ThreatByte Portal</a>\n\n"
        "<i>Stay vigilant! Type /today anytime to request the latest daily briefing.</i>"
    )
    send_telegram_message(welcome_text, chat_id=str(chat_id))

def format_telegram_digest(articles: List[Dict[str, Any]], date_str: str, site_url: str = SITE_URL) -> List[str]:
    """
    Format enriched cyber intelligence items into a human-readable,
    editorial morning dispatch.
    """
    if not articles:
        return ["⚠️ <b>ThreatByte Daily Briefing</b>: No major critical incidents reported in this cycle."]

    severity_emojis = {
        "CRITICAL": "🔴 <b>[CRITICAL]</b>",
        "HIGH": "🟠 <b>[HIGH]</b>",
        "MEDIUM": "🟡 <b>[MEDIUM]</b>",
        "LOW": "🟢 <b>[LOW]</b>"
    }

    # Header
    header = (
        f"🛡️ <b>THREATBYTE // MORNING BRIEFING</b>\n"
        f"📅 <i>{escape_html(date_str)} Edition</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    items_to_send = articles[:TOP_STORIES_FOR_TELEGRAM]
    chunks = []
    current_chunk = header

    for idx, item in enumerate(items_to_send, 1):
        sev = item.get("severity", "HIGH").upper()
        sev_tag = severity_emojis.get(sev, "🟠 <b>[HIGH]</b>")
        category = escape_html(item.get("threat_category", "Security Incident"))
        title = escape_html(item.get("title", "Untitled"))
        url = item.get("url", "#")
        source = escape_html(item.get("source", "CTI Feed"))
        cves = item.get("cve_ids", [])
        snippet = escape_html(item.get("telegram_snippet", item.get("executive_summary", "")))
        
        cve_tag = f" | <code>{', '.join(cves)}</code>" if cves else ""

        entry_text = (
            f"<b>{idx}.</b> {sev_tag} <b>{category}</b>{cve_tag}\n"
            f"📰 <b><a href=\"{url}\">{title}</a></b>\n"
            f"🔍 {snippet}\n"
            f"📡 <i>Source: {source}</i>\n\n"
        )

        if len(current_chunk) + len(entry_text) > 3500:
            chunks.append(current_chunk)
            current_chunk = f"🛡️ <b>THREATBYTE INTEL (Cont'd)</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n" + entry_text
        else:
            current_chunk += entry_text

    # Footer
    footer = (
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🌐 <b>Read Full Deep-Dive Analysis & Mitigations:</b>\n"
        f"👉 <a href=\"{site_url}\">Open ThreatByte Dashboard</a>\n\n"
        f"🔔 <i>Invite colleagues: @{TELEGRAM_BOT_USERNAME}</i>"
    )

    if len(current_chunk) + len(footer) > 4000:
        chunks.append(current_chunk)
        chunks.append(footer)
    else:
        current_chunk += footer
        chunks.append(current_chunk)

    return chunks

def send_telegram_message(text: str, chat_id: str, bot_token: str = TELEGRAM_BOT_TOKEN) -> bool:
    """Send an HTML-formatted message to a specific Telegram chat_id."""
    if not bot_token or not chat_id:
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }

    try:
        resp = requests.post(url, json=payload, timeout=15)
        if resp.status_code == 200:
            return True
        else:
            print(f"[!] Telegram API error for chat {chat_id} ({resp.status_code}): {resp.text}")
            return False
    except Exception as e:
        print(f"[!] Exception sending Telegram message to {chat_id}: {e}")
        return False

def broadcast_daily_briefing(articles: List[Dict[str, Any]], date_str: str) -> bool:
    """
    Main broadcast entrypoint.
    1. Syncs all users who interacted with the bot.
    2. Broadcasts the daily briefing to all active subscribers & configured channels.
    """
    # 1. Sync any new subscribers
    new_count = sync_telegram_subscribers()
    if new_count > 0:
        print(f"[*] Registered {new_count} new subscriber(s) before broadcast.")

    chunks = format_telegram_digest(articles, date_str)
    subscribers = load_subscribers()
    target_chats: Set[str] = {str(s["chat_id"]) for s in subscribers if s.get("active", True)}

    # Add default configured channel or chat ID if specified in env
    if TELEGRAM_CHAT_ID:
        target_chats.add(TELEGRAM_CHAT_ID)

    if not TELEGRAM_BOT_TOKEN:
        print("\n" + "="*50)
        print("[SIMULATION] Telegram Bot Token not set.")
        print(f"Would broadcast to {len(target_chats)} subscribers:")
        for idx, chunk in enumerate(chunks, 1):
            print(chunk)
        print("="*50)
        return True

    if not target_chats:
        print(f"[*] No subscribers yet in data/subscribers.json.")
        print(f"    Users can start receiving broadcasts by opening: https://t.me/{TELEGRAM_BOT_USERNAME} and pressing START.")
        return True

    print(f"[*] Broadcasting daily briefing ({len(chunks)} parts) to {len(target_chats)} subscriber(s)...")
    success_count = 0
    for chat_id in target_chats:
        sent_all = True
        for chunk in chunks:
            if not send_telegram_message(chunk, chat_id=chat_id):
                sent_all = False
        if sent_all:
            success_count += 1

    print(f"[+] Broadcast complete: Successfully delivered to {success_count}/{len(target_chats)} chats.")
    return success_count > 0

if __name__ == "__main__":
    sync_telegram_subscribers()
    subs = load_subscribers()
    print(f"Current subscribers count: {len(subs)}")
