"""Simple scheduler — runs the pipeline at configured times each day.

Usage:
    python scheduler.py

This runs continuously and triggers the pipeline at the scheduled times.
For production, prefer Windows Task Scheduler or cron instead.
"""

import time
import schedule
from datetime import datetime
from src.pipeline import run_pipeline


def job():
    """Scheduled job wrapper with error handling."""
    print(f"\n{'='*50}")
    print(f"Scheduled run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")
    try:
        run_pipeline()
    except Exception as e:
        print(f"Pipeline error (will retry next scheduled run): {e}")


# Schedule 1 post per day — evening peak hour
schedule.every().day.at("19:00").do(job)

print("Scheduler started. Videos will be generated at 19:00 daily.")
print("Press Ctrl+C to stop.\n")

while True:
    schedule.run_pending()
    time.sleep(60)
