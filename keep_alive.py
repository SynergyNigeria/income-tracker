"""
Keep-Alive script for Render free tier.

Render spins down free web services after 15 minutes of inactivity.
Run this script locally (or anywhere) to ping your site every 14 minutes
so it never goes to sleep.

Usage:
    python keep_alive.py

Set your site URL below or pass it as an environment variable:
    SITE_URL=https://your-app.onrender.com python keep_alive.py
"""

import os
import time
import urllib.request
import urllib.error
from datetime import datetime

# ── CONFIG ────────────────────────────────────────────────────────────────────
SITE_URL = os.environ.get("SITE_URL", "https://my-income-tracker.onrender.com")
PING_INTERVAL_SECONDS = 14 * 60  # 14 minutes
# ─────────────────────────────────────────────────────────────────────────────


def ping(url: str) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            print(f"[{now}] ✅  Pinged {url} — HTTP {response.status}")
    except urllib.error.HTTPError as e:
        # 4xx/5xx still means the server is awake
        print(f"[{now}] ⚠️  Pinged {url} — HTTP {e.code} (server is up)")
    except Exception as e:
        print(f"[{now}] ❌  Failed to ping {url}: {e}")


def main() -> None:
    print(f"Keep-alive started. Pinging {SITE_URL} every {PING_INTERVAL_SECONDS // 60} minutes.")
    print("Press Ctrl+C to stop.\n")
    while True:
        ping(SITE_URL)
        time.sleep(PING_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
