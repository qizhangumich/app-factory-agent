"""Revenue tracker — folds per-app earnings into accounts and system totals.

In production this is fed by App Store Connect / Google Play sales reports
(pulled by scripts/update_revenue.sh). It exposes a single ``record_revenue``
entry point plus an aggregate ``refresh`` used by the brain each cycle.
"""
from __future__ import annotations

from datetime import datetime, timezone

from . import state_io


def record_revenue(workspace_id: str, account_id: str, amount_usd: float,
                    day: str | None = None) -> None:
    """Record a revenue event for one app on one day and roll up totals."""
    day = day or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    revenue = state_io.load_state("revenue")

    revenue["by_app"][workspace_id] = round(
        revenue["by_app"].get(workspace_id, 0) + amount_usd, 2)
    revenue["by_account"][account_id] = round(
        revenue["by_account"].get(account_id, 0) + amount_usd, 2)

    daily = {d["date"]: d for d in revenue["daily"]}
    entry = daily.setdefault(day, {"date": day, "amount": 0})
    entry["amount"] = round(entry["amount"] + amount_usd, 2)
    revenue["daily"] = sorted(daily.values(), key=lambda d: d["date"])

    revenue["totals"]["all_time"] = round(
        revenue["totals"]["all_time"] + amount_usd, 2)
    state_io.save_state("revenue", revenue)

    _apply_to_account(account_id, amount_usd)
    _apply_to_app(workspace_id, amount_usd)


def _apply_to_account(account_id: str, amount_usd: float) -> None:
    accounts = state_io.load_state("accounts")
    for account in accounts["accounts"]:
        if account["id"] == account_id:
            account["total_earned"] = round(
                account.get("total_earned", 0) + amount_usd, 2)
            break
    state_io.save_state("accounts", accounts)


def _apply_to_app(workspace_id: str, amount_usd: float) -> None:
    apps = state_io.load_state("apps")
    for app in apps["apps"]:
        if app["workspace_id"] == workspace_id:
            app["revenue_total"] = round(
                app.get("revenue_total", 0) + amount_usd, 2)
            break
    state_io.save_state("apps", apps)


def refresh() -> dict:
    """Recompute system-level revenue rollups and breakeven flag.

    Returns a small summary dict for the brain's decision log.
    """
    revenue = state_io.load_state("revenue")
    state = state_io.load_state("state")
    total = revenue["totals"]["all_time"]

    state["revenue"]["total_earned"] = total
    state["revenue"]["breakeven_reached"] = total >= state["revenue"]["breakeven_target"]
    state_io.save_state("state", state)

    return {
        "total_earned": total,
        "breakeven_reached": state["revenue"]["breakeven_reached"],
    }
