"""Account manager — tracks the 12 developer accounts and assigns apps.

Decides which of the 6 iOS + 6 Android accounts owns a given app, balances
load by category, and freezes accounts that have earned $0 for too long.
"""
from __future__ import annotations

from datetime import datetime, timezone

from . import state_io

# Category -> account allocation (mirrors config/accounts_config.yaml).
IOS_ALLOCATION = {
    "Utilities": "ios_001", "Productivity": "ios_001", "Lifestyle": "ios_001",
    "Health & Fitness": "ios_002", "Health": "ios_002",
    "Education": "ios_003", "Reference": "ios_003",
    "Photography": "ios_004", "Photo": "ios_004", "Creative": "ios_004", "Music": "ios_004",
    "Custom": "ios_005",
}
ANDROID_ALLOCATION = {
    "Utilities": "android_001", "Productivity": "android_001", "Lifestyle": "android_001",
    "Health & Fitness": "android_002", "Health": "android_002",
    "Education": "android_002", "Reference": "android_002",
    "Photography": "android_003", "Photo": "android_003", "Creative": "android_003", "Music": "android_003",
    "Custom": "android_004",
}
IOS_OVERFLOW = "ios_006"
ANDROID_OVERFLOW = "android_005"

FREEZE_AFTER_DAYS_ZERO = 60


def normalize_account_id(account_id: str) -> str:
    """Map the short ``and_00X`` spec form onto the canonical ``android_00X``."""
    if account_id and account_id.startswith("and_") and not account_id.startswith("android_"):
        return "android_" + account_id[len("and_"):]
    return account_id


def _accounts_by_id(accounts_doc: dict) -> dict:
    return {a["id"]: a for a in accounts_doc["accounts"]}


def assign_account(category: str, platform: str, accounts_doc: dict | None = None) -> str:
    """Return the account ID that should own an app of ``category`` on ``platform``.

    Falls back to the overflow account when the primary account is frozen.
    """
    if accounts_doc is None:
        accounts_doc = state_io.load_state("accounts")
    by_id = _accounts_by_id(accounts_doc)

    if platform == "ios":
        account_id = IOS_ALLOCATION.get(category, IOS_OVERFLOW)
        overflow = IOS_OVERFLOW
    else:
        account_id = ANDROID_ALLOCATION.get(category, ANDROID_OVERFLOW)
        overflow = ANDROID_OVERFLOW

    account = by_id.get(account_id)
    if account is None or account.get("status") == "frozen":
        return overflow
    return account_id


def check_health(accounts_doc: dict | None = None) -> list[dict]:
    """Freeze accounts that have earned $0 for ``FREEZE_AFTER_DAYS_ZERO`` days.

    Returns a list of {account_id, action} changes for the decision log.
    """
    if accounts_doc is None:
        accounts_doc = state_io.load_state("accounts")
    changes: list[dict] = []
    now = datetime.now(timezone.utc)

    for account in accounts_doc["accounts"]:
        if account.get("status") != "active":
            continue
        if account.get("total_earned", 0) > 0:
            continue
        first_app = account.get("first_app_at")
        if not first_app:
            continue
        age_days = (now - _parse(first_app)).days
        if age_days >= FREEZE_AFTER_DAYS_ZERO and not account.get("apps"):
            continue
        if age_days >= FREEZE_AFTER_DAYS_ZERO:
            account["status"] = "frozen"
            changes.append({"account_id": account["id"], "action": "frozen_zero_revenue"})

    if changes:
        state_io.save_state("accounts", accounts_doc)
    return changes


def _parse(iso: str) -> datetime:
    return datetime.strptime(iso.replace("Z", "+0000"), "%Y-%m-%dT%H:%M:%S%z")
