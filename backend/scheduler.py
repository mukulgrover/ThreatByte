"""
Autonomous Background Scheduler Daemon for ThreatByte CTI Pipeline.
Runs locally or on a VPS/server, triggering daily ingestion, AI reasoning,
dashboard file updates, and Telegram broadcasts at 08:00 AM IST (02:30 UTC).
"""
import sys
import time
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Ensure root directory is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.generator import run_daily_pipeline

def check_and_run_daily(target_hour_utc: int = 2, target_minute_utc: int = 30):
    """
    Continuous loop that runs the pipeline when the target time is reached
    and ensures only 1 execution per calendar day.
    """
    last_run_date = None
    print(f"[*] ThreatByte Autonomous Scheduler started.")
    print(f"[*] Scheduled time: {target_hour_utc:02d}:{target_minute_utc:02d} UTC (08:00 AM IST) daily.")

    while True:
        try:
            now = datetime.now(timezone.utc)
            today_str = now.strftime("%Y-%m-%d")

            # Check if target time reached and not already executed today
            is_time_to_run = (
                (now.hour > target_hour_utc or (now.hour == target_hour_utc and now.minute >= target_minute_utc))
                and last_run_date != today_str
            )

            if is_time_to_run:
                print(f"\n[🚀 SCHEDULER TRIGGER] Running daily CTI pipeline for {today_str} at {now.strftime('%H:%M:%S UTC')}...")
                try:
                    run_daily_pipeline()
                    last_run_date = today_str
                    print(f"[+] Daily briefing for {today_str} complete.")
                except Exception as ex:
                    print(f"[!] Pipeline error: {ex}")

            time.sleep(30)  # Check every 30 seconds

        except KeyboardInterrupt:
            print("\n[*] Scheduler stopped by user.")
            break
        except Exception as e:
            print(f"[!] Scheduler loop exception: {e}")
            time.sleep(60)

if __name__ == "__main__":
    check_and_run_daily()
