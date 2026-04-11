#!/usr/bin/env python3
"""
main.py — Orchestrator
Runs the full pipeline: scrape → sync to Google Sheets → notify.
Used by both local dev and GitHub Actions.
"""

import argparse
import json
import os
import sys
import traceback

from config import SESSION_ID
from scraper import DEFAULT_LOOKBACK_HOURS


def main():
    parser = argparse.ArgumentParser(description="Job Tracker — scrape & sync")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Scrape but don't write to Google Sheets (print only)",
    )
    parser.add_argument(
        "--scrape-only",
        action="store_true",
        help="Scrape and save to local JSON, skip Sheets sync",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=50,
        help="Maximum number of pages to scrape (default: 50)",
    )
    parser.add_argument(
        "--lookback-hours",
        type=int,
        default=None,
        help="Lookback window in hours (default: 336 = 14 days). Use 1 for quick test, 8 for daily cron.",
    )
    args = parser.parse_args()

    # ── Compute lookback label for notifications ──
    hours = args.lookback_hours if args.lookback_hours is not None else DEFAULT_LOOKBACK_HOURS
    lookback_label = f"{hours}h" if hours < 48 else f"{hours // 24}d"

    # ── Resolve session ID ──
    session_id = os.environ.get("JOBRIGHT_SESSION_ID", SESSION_ID)
    if not session_id:
        print("❌  JOBRIGHT_SESSION_ID is not set.")
        print("   Export it:  export JOBRIGHT_SESSION_ID='your_session_id'")
        sys.exit(1)

    try:
        # ── Phase 3: Scrape ──
        from scraper import scrape_all
        jobs = scrape_all(session_id, max_pages=args.max_pages, lookback_hours=args.lookback_hours)

        if not jobs:
            print("ℹ️  No jobs found. Exiting.")
            return

        # ── Save local backup ──
        backup = "scraped_jobs.json"
        with open(backup, "w", encoding="utf-8") as f:
            json.dump(jobs, f, ensure_ascii=False, indent=2)
        print(f"💾  Local backup → {backup}")

        if args.scrape_only:
            print("📋  --scrape-only mode. Skipping Sheets sync.")
            return

        # ── Phase 4: Sync to Sheets ──
        from sheets_sync import sync_to_sheets
        stats, new_jobs = sync_to_sheets(jobs, dry_run=args.dry_run)

        print("\n🎉  Pipeline complete!")

        # ── Notify on success ──
        from notifier import notify_success
        notify_success(stats, len(jobs), lookback_label, new_jobs=new_jobs)

    except SystemExit:
        # scraper calls sys.exit(1) on 401/403 — catch and notify
        from notifier import notify_error
        notify_error("SESSION_ID expired (HTTP 401/403). Re-export from browser and update GitHub Secret.")
        raise
    except Exception:
        from notifier import notify_error
        notify_error(traceback.format_exc()[-500:])
        raise


if __name__ == "__main__":
    main()
