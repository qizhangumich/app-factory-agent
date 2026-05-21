"""Pricing optimizer — picks an App Store price tier per app category.

Standard apps map category + effort to a tier; the per-country price points
are then derived from Apple's tier table in config/apple_price_tiers.json.
"""
from __future__ import annotations

import json
import os

from . import state_io

# Category -> default tier for a standard (non-custom) app.
CATEGORY_TIER = {
    "Utilities": 1,
    "Productivity": 2,
    "Lifestyle": 1,
    "Health & Fitness": 2,
    "Health": 2,
    "Education": 2,
    "Reference": 2,
    "Photography": 3,
    "Photo": 3,
    "Creative": 3,
    "Music": 2,
    "Custom": 5,
}


def _tier_table() -> dict:
    path = os.path.join(state_io.CONFIG_DIR, "apple_price_tiers.json")
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)["tiers"]


def pick_tier(idea: dict) -> int:
    """Choose a price tier, nudging up for high build effort."""
    tier = CATEGORY_TIER.get(idea.get("category", ""), 2)
    if idea.get("estimated_build_hours", 0) >= 8 and tier < 3:
        tier += 1
    return tier


def price_for_tier(tier: int) -> float:
    return float(_tier_table().get(str(tier), 0.0))


def optimize(idea: dict) -> dict:
    """Return {'price_tier': int, 'price_usd': float} for an idea."""
    tier = idea.get("price_tier") or pick_tier(idea)
    return {"price_tier": tier, "price_usd": price_for_tier(tier)}
