#!/usr/bin/env python3
"""
App Factory v2 — Daily revenue refresh (Layer 1 closing the loop)
=====================================================================
Pulls one day's sales from Apple + Google Play, folds each row through
revenue_tracker.record_revenue, then runs the brain's downstream
modules (kill_boost, localization_planner) on the updated state.

Designed to run as a cron — once a day after Apple publishes the
prior day's report (around 8am Pacific).

Usage:
    python scripts/refresh_revenue.py                # yesterday's data
    python scripts/refresh_revenue.py --date 2026-06-25
    python scripts/refresh_revenue.py --dry-run      # fetch but don't record

What it does NOT do yet:
    - Google Play sales (Phase 1 apps are free + no IAP; see
      brain/play_sales_fetcher.py for the wiring plan)
    - Pricing optimization (needs >1 month of data per app)
    - Auto-create new spec.json from app_scorer (Day-3 curriculum)
"""

import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Make `brain` importable when running from repo root
sys.path.insert(0, str(Path(__file__).parent.parent))

from brain import apple_sales_fetcher, play_sales_fetcher, state_io
from brain import revenue_tracker, kill_boost


def banner(msg: str) -> None:
    print(f"\n{'='*60}\n  {msg}\n{'='*60}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="YYYY-MM-DD; default: yesterday UTC")
    ap.add_argument("--dry-run", action="store_true",
                    help="fetch but don't write to state files")
    args = ap.parse_args()

    target_date = args.date or (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    banner(f"Daily revenue refresh — {target_date}")

    # --- Apple ---
    print("\n[Apple App Store]")
    try:
        events = apple_sales_fetcher.fetch_sales(target_date)
        enriched = apple_sales_fetcher.map_to_workspace(events)
    except SystemExit as e:
        print(f"  skip: {e}")
        enriched = []

    apple_total = 0.0
    apple_rows  = 0
    for ev in enriched:
        if not ev.get("workspace_id") or not ev.get("account_id"):
            print(f"  WARN: unmapped Apple Id {ev['apple_identifier']} — skipping")
            continue
        if not args.dry_run:
            revenue_tracker.record_revenue(
                workspace_id=ev["workspace_id"],
                account_id=ev["account_id"],
                amount_usd=ev["proceeds_usd"],
                day=ev["date"][:10] if len(ev["date"]) >= 10 else target_date,
            )
        apple_total += ev["proceeds_usd"]
        apple_rows  += 1
        print(f"  {ev['workspace_id']:10}  units={ev['units']:>4}  "
              f"proceeds=${ev['proceeds_usd']:>7.2f}  {ev['country']:3}  {ev['title']}")
    print(f"  → {apple_rows} row(s), ${apple_total:.2f} total")

    # --- Google Play ---
    print("\n[Google Play]")
    play_events = play_sales_fetcher.fetch_sales(target_date)
    print(f"  → {len(play_events)} row(s) (Play fetcher is currently a stub —"
          " see brain/play_sales_fetcher.py)")

    # --- Roll up ---
    if args.dry_run:
        print("\n[dry-run] skipping revenue refresh + kill/boost")
        return

    banner("Brain rollup")
    summary = revenue_tracker.refresh()
    print(f"  Total earned all-time: ${summary['total_earned']:.2f}")
    print(f"  Breakeven reached:     {summary['breakeven_reached']}")

    # --- Kill / boost engine ---
    banner("Kill / boost evaluation")
    try:
        kb_summary = kill_boost.run()
        print(f"  Killed:  {kb_summary.get('killed', [])}")
        print(f"  Boosted: {kb_summary.get('boosted', [])}")
    except Exception as e:
        print(f"  skip: {e}")

    print()


if __name__ == "__main__":
    main()
