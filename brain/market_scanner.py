"""Market scanner — finds opportunities and turns them into build specs.

In production this analyses data/ranks.csv (global paid-app rankings) to find
under-served niches. Until that dataset is loaded, it draws from a curated
idea backlog so the queue never starves.
"""
from __future__ import annotations

import os

from . import app_scorer, state_io

# Curated backlog beyond the pre-loaded 24-app manifest. Each entry is a
# lightweight idea; the brain expands a winner into a full spec.json.
IDEA_BACKLOG = [
    {"app_name": "Screen Ruler & Measure", "slug": "screenruler", "category": "Utilities",
     "platforms": ["ios"], "estimated_build_hours": 5, "languages": ["en", "de"]},
    {"app_name": "Color Picker & Palette", "slug": "colorpicker", "category": "Photo",
     "platforms": ["ios"], "estimated_build_hours": 5, "languages": ["en"]},
    {"app_name": "Morse Code Translator", "slug": "morsecode", "category": "Education",
     "platforms": ["ios", "android"], "estimated_build_hours": 4, "languages": ["en"]},
    {"app_name": "BMI & Body Fat Calc", "slug": "bmicalc", "category": "Health",
     "platforms": ["ios", "android"], "estimated_build_hours": 5, "languages": ["en", "ja"]},
    {"app_name": "Day Counter & Countdown", "slug": "daycounter", "category": "Lifestyle",
     "platforms": ["ios", "android"], "estimated_build_hours": 6, "languages": ["en", "ja", "ko"]},
]


def has_ranks_data() -> bool:
    return os.path.exists(os.path.join(state_io.DATA_DIR, "ranks.csv"))


def scan(limit: int = 5) -> list[dict]:
    """Return up to ``limit`` scored ideas that pass the score gate.

    Already-specced slugs (anything in apps.json) are skipped so the scanner
    never proposes a duplicate.
    """
    existing = {a["slug"] for a in state_io.load_state("apps")["apps"]}
    results: list[dict] = []
    for idea in IDEA_BACKLOG:
        if idea["slug"] in existing:
            continue
        scored = app_scorer.score_idea(idea)
        if scored["pass"]:
            enriched = dict(idea)
            enriched["score"] = scored["score"]
            enriched["score_breakdown"] = scored["breakdown"]
            results.append(enriched)
        if len(results) >= limit:
            break
    results.sort(key=lambda i: i["score"], reverse=True)
    return results
