"""
Standalone Interactive Bot Listener for ThreatByte.
Runs a continuous polling listener to instantly welcome new subscribers and reply to commands (/today, /help).
"""
import time
import sys
import json
import requests
from pathlib import Path

# Ensure repository root is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.config import TELEGRAM_BOT_TOKEN, TELEGRAM_BOT_USERNAME, SITE_URL, DATA_DIR
from backend.telegram_bot import register_subscriber, send_welcome_message, send_telegram_message, format_telegram_digest

def load_latest_payload():
    """Load latest generated intelligence payload."""
    latest_file = DATA_DIR / "latest.json"
    if latest_file.exists():
        try:
            with open(latest_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None

def start_bot_polling():
    """Poll for incoming commands and reply instantly."""
    if not TELEGRAM_BOT_TOKEN:
        print("[!] No TELEGRAM_BOT_TOKEN found in environment.")
        return

    print(f"[*] ThreatByte Telegram Bot Service active (@{TELEGRAM_BOT_USERNAME}). Listening for subscribers...")
    offset = None

    while True:
        try:
            params = {"timeout": 30}
            if offset is not None:
                params["offset"] = offset

            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
            resp = requests.get(url, params=params, timeout=35)
            if resp.status_code != 200:
                time.sleep(3)
                continue

            data = resp.json()
            updates = data.get("result", [])

            for u in updates:
                offset = u["update_id"] + 1
                msg = u.get("message") or u.get("channel_post")
                if not msg:
                    continue

                chat = msg.get("chat", {})
                chat_id = chat.get("id")
                from_user = msg.get("from", {})
                text = (msg.get("text") or "").strip().lower()

                if not chat_id:
                    continue

                # Register user
                register_subscriber(chat_id, {
                    "first_name": from_user.get("first_name") or chat.get("title") or "Subscriber",
                    "username": from_user.get("username") or "",
                    "date": str(msg.get("date", ""))
                })

                # Handle commands
                if text.startswith("/start") or text.startswith("/subscribe"):
                    send_welcome_message(chat_id)
                elif text.startswith("/today") or text.startswith("/latest") or text.startswith("/news"):
                    payload = load_latest_payload()
                    if payload and payload.get("articles"):
                        chunks = format_telegram_digest(payload["articles"], payload.get("date", "Today"))
                        for chunk in chunks:
                            send_telegram_message(chunk, chat_id=str(chat_id))
                    else:
                        send_telegram_message("⏳ ThreatByte is gathering today's threat telemetry. Please check back shortly!", chat_id=str(chat_id))
                elif text.startswith("/help"):
                    help_msg = (
                        "🛡️ <b>ThreatByte Bot Commands:</b>\n\n"
                        "• /today - Get today's breaking threat intelligence dispatch\n"
                        "• /subscribe - Ensure you are registered for 06:00 UTC morning bulletins\n"
                        "• /help - Display this command menu\n\n"
                        f"🌐 Web Portal: {SITE_URL}"
                    )
                    send_telegram_message(help_msg, chat_id=str(chat_id))

        except Exception as e:
            time.sleep(3)

if __name__ == "__main__":
    start_bot_polling()
