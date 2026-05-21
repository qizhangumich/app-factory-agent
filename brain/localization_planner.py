"""Localization planner — picks which languages an app ships in.

Phased rollout: English first for speed, then Japanese and German for
top performers, widening to the full 10-language set for proven winners.
"""
from __future__ import annotations

# Languages ordered by iOS revenue share (see instruction book section 15).
PRIORITY = ["en", "ja", "de", "ko", "zh-Hans", "fr", "es", "pt", "zh-Hant", "ar"]

PHASE_LANGUAGES = {
    "launch": ["en"],
    "validated": ["en", "ja", "de"],
    "winner": PRIORITY,
}


def plan_languages(idea: dict, phase: str = "launch") -> list[str]:
    """Return the language list for an app given its rollout ``phase``.

    A spec may pin its own ``languages``; that always takes precedence.
    """
    pinned = idea.get("languages")
    if pinned:
        return pinned
    return PHASE_LANGUAGES.get(phase, ["en"])


def expansion_for_winner(app: dict) -> list[str]:
    """Languages to add when an app is flagged as a winner."""
    current = set(app.get("languages", ["en"]))
    return [lang for lang in PRIORITY if lang not in current]
