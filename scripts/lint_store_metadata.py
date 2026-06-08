#!/usr/bin/env python3
"""
App Factory v2 — Store Metadata Policy Linter
==============================================
Scans every app's title.txt / short_description.txt / full_description.txt
for phrases that violate Google Play's Metadata Policy (superlatives,
ranking claims, awards, comparison claims).

Run BEFORE every  python scripts/play_release.py --submit  so reviewers
never see a banned phrase.

Exit code 0 = clean, 1 = violations found.

Usage:
    python scripts/lint_store_metadata.py
    python scripts/lint_store_metadata.py --ws ws_001_tipcalcdeluxe
"""

import re, sys, argparse
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()

# Phrases Google's Metadata Policy specifically calls out plus common variants.
# Source: https://support.google.com/googleplay/android-developer/answer/9898842
# (Metadata policy: no performance/ranking/award/superlative claims)
# Confirmed-rejection patterns. Each one matches a real Play review
# rejection we've seen or that Google's policy doc directly names.
# Descriptive functionality words like "instantly" or "fast" are allowed
# because they describe what the app does, not how it ranks.
BANNED_PATTERNS = [
    (r"\bfastest\b",                "superlative speed claim — Google rejected ws_001 for this exact word"),
    (r"\bbest\b",                   "superlative comparison — Google's policy doc lists this explicitly"),
    (r"\btop\b",                    "ranking claim — Google's policy doc lists this explicitly"),
    (r"\b#\s*1\b",                  "ranking claim — Google's policy doc lists this explicitly"),
    (r"\b#1\b",                     "ranking claim"),
    (r"\bnumber one\b",             "ranking claim"),
    (r"\bworld'?s\b",               "comparative scope claim"),
    (r"\bleading\b",                "ranking claim"),
    (r"\bultimate\b",               "superlative"),
    (r"\bperfect\b",                "superlative — 'perfect time' rejected ws_005"),
    (r"\bmost (?:accurate|powerful|advanced|popular|complete|reliable)\b",
                                    "superlative + dimension"),
    (r"\baward[- ]winning\b",       "award claim"),
    (r"\bapp of the (?:year|day|week|month)\b", "Play Store program claim — Google's policy doc lists this explicitly"),
    (r"\b(?:editor|editors)['']? choice\b", "Play Store program claim"),
    (r"\bever\b",                   "absolute claim ('best ever', 'no ads ever') — rejected ws_005"),
    (r"\bonly app\b",               "uniqueness claim"),
    (r"\b(?:the )?(?:one|sole) (?:and only )?app\b", "uniqueness claim"),
    (r"\b(?:5|five)[- ]?stars?\b",  "rating claim"),
    (r"\bguaranteed\b",             "absolute claim"),
]

# Files to lint, per workspace
FILES = ["title.txt", "short_description.txt", "full_description.txt"]


def discover_workspaces():
    return sorted(
        p.name for p in (REPO_ROOT / "workspaces").iterdir()
        if p.is_dir() and (p / "android" / "fastlane" / "metadata" / "android" / "en-US").exists()
    )


def lint_file(path: Path):
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="ignore")
    hits = []
    for pattern, reason in BANNED_PATTERNS:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            start = max(0, m.start() - 30)
            end   = min(len(text), m.end() + 30)
            snippet = text[start:end].replace("\n", " ").strip()
            hits.append({
                "phrase":  m.group(),
                "reason":  reason,
                "snippet": snippet,
            })
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ws", help="lint only this workspace (e.g. ws_001_tipcalcdeluxe)")
    args = ap.parse_args()

    workspaces = [args.ws] if args.ws else discover_workspaces()
    total_violations = 0

    for ws in workspaces:
        md = REPO_ROOT / "workspaces" / ws / "android" / "fastlane" / "metadata" / "android" / "en-US"
        if not md.exists():
            continue
        ws_hits = 0
        printed_header = False
        for fname in FILES:
            hits = lint_file(md / fname)
            if hits and not printed_header:
                print(f"\n=== {ws} ===")
                printed_header = True
            for h in hits:
                print(f"  [{fname}] '{h['phrase']}' ({h['reason']})")
                print(f"     -> ...{h['snippet']}...")
                ws_hits += 1
        total_violations += ws_hits

    print()
    if total_violations == 0:
        print(f"[OK] No metadata policy violations across {len(workspaces)} workspace(s).")
        sys.exit(0)
    else:
        print(f"[FAIL] {total_violations} violation(s) found. Fix before submitting to Play.")
        print("\nReference: https://support.google.com/googleplay/android-developer/answer/9898842")
        sys.exit(1)


if __name__ == "__main__":
    main()
