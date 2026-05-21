"""Kill / boost engine — prunes dead apps and flags winners.

- Apps live >= 30 days with $0 revenue are killed.
- Apps earning >= $10 in their first week are flagged for localization
  expansion (a "boost").
"""
from __future__ import annotations

from datetime import datetime, timezone

from . import state_io

KILL_AFTER_DAYS_ZERO = 30
BOOST_WEEK1_USD = 10.0


def run() -> dict:
    """Scan all apps; kill the dead, flag the winners. Returns a summary."""
    apps = state_io.load_state("apps")
    now = datetime.now(timezone.utc)
    killed, boosted = [], []

    for app in apps["apps"]:
        if app.get("killed") or not app.get("live_at"):
            continue
        live_days = (now - _parse(app["live_at"])).days
        revenue = app.get("revenue_total", 0)

        if live_days >= KILL_AFTER_DAYS_ZERO and revenue == 0:
            app["killed"] = True
            app["status"] = "killed"
            app["killed_at"] = state_io.now_iso()
            killed.append(app["workspace_id"])
            continue

        if live_days <= 7 and revenue >= BOOST_WEEK1_USD and not app.get("boosted"):
            app["boosted"] = True
            app["status"] = "boost_localize"
            boosted.append(app["workspace_id"])

    if killed or boosted:
        state_io.save_state("apps", apps)

    if killed:
        state = state_io.load_state("state")
        state["counters"]["apps_killed"] = state["counters"].get("apps_killed", 0) + len(killed)
        state_io.save_state("state", state)

    return {"killed": killed, "boosted": boosted}


def _parse(iso: str) -> datetime:
    return datetime.strptime(iso.replace("Z", "+0000"), "%Y-%m-%dT%H:%M:%S%z")
