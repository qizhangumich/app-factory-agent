"""App scorer — scores app ideas on 5 weighted dimensions.

The brain only builds ideas that clear ``MIN_SCORE``. Each dimension is
0-10; the total is the weighted sum (max 50).
"""
from __future__ import annotations

WEIGHTS = {
    "revenue_potential": 1.0,   # estimated demand x willingness-to-pay
    "build_speed": 1.0,         # 10 = trivial, 0 = 80h custom app
    "low_competition": 1.0,     # 10 = wide-open niche
    "easy_localization": 1.0,   # 10 = little/no text, trivial to localize
    "low_maintenance": 1.0,     # 10 = no servers, no API drift
}
MAX_SCORE = 50.0
MIN_SCORE = 30.0


def score_idea(idea: dict) -> dict:
    """Return {'score': float, 'breakdown': {...}, 'pass': bool}.

    If the idea already carries a ``score_breakdown`` (pre-scored specs from
    the launch manifest) it is used directly; otherwise heuristics apply.
    """
    breakdown = idea.get("score_breakdown") or _heuristic_breakdown(idea)
    total = round(sum(breakdown.get(k, 0) * w for k, w in WEIGHTS.items()), 1)
    return {"score": total, "breakdown": breakdown, "pass": total >= MIN_SCORE}


def _heuristic_breakdown(idea: dict) -> dict:
    hours = idea.get("estimated_build_hours", 8)
    build_speed = max(0.0, min(10.0, 10.0 - hours / 8.0))
    requires_server = idea.get("requires_server", False)
    languages = idea.get("languages", ["en"])
    easy_loc = 10.0 if len(languages) <= 1 else max(2.0, 10.0 - len(languages))
    return {
        "revenue_potential": 6.0,
        "build_speed": round(build_speed, 1),
        "low_competition": 3.0,
        "easy_localization": round(easy_loc, 1),
        "low_maintenance": 4.0 if requires_server else 10.0,
    }
