#!/usr/bin/env python3
"""
App Factory v2 - Print Standard Play Content Declarations
==========================================================
Reads config/play_content_declarations.yaml and prints a copy-paste-ready
answer sheet for a given app's "App content" declarations in Play Console.

Usage:
    python scripts/print_declarations.py                    # all apps
    python scripts/print_declarations.py ws_001_tipcalcdeluxe   # one app
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
CONFIG    = REPO_ROOT / "config" / "play_content_declarations.yaml"

APPS = [
    ("ws_001_tipcalcdeluxe",    "Tip Calculator Deluxe", "tipcalcdeluxe"),
    ("ws_002_unitconverterpro", "Unit Converter Pro",    "unitconverterpro"),
    ("ws_004_qrbarcodescanner", "QR & Barcode Scanner+", "qrbarcodescanner"),
    ("ws_005_pomodorofocus",    "Pomodoro Focus Timer",  "pomodorofocus"),
]


def load_config():
    try:
        import yaml
    except ImportError:
        print("Install pyyaml first:  pip install pyyaml")
        sys.exit(1)
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))


def merged(cfg, ws):
    """Return config with per-app overrides applied."""
    overrides = (cfg.get("overrides") or {}).get(ws, {}) or {}
    result = {}
    for k, v in cfg.items():
        if k == "overrides":
            continue
        if isinstance(v, dict) and k in overrides:
            result[k] = {**v, **overrides[k]}
        else:
            result[k] = v
    return result


def print_app(cfg, ws, name, slug):
    m = merged(cfg, ws)
    base = m["privacy_policy"]["base_url"]

    print(f"\n{'='*68}")
    print(f"  {name}  ({ws})")
    print('='*68)

    print(f"\n  1. PRIVACY POLICY")
    print(f"     URL: {base}/{slug}.html")

    print(f"\n  2. ADS")
    print(f"     Does your app contain ads? -> {'Yes' if m['ads']['contains_ads'] else 'No'}")

    print(f"\n  3. APP ACCESS")
    print(f"     -> All functionality is available without special access")

    print(f"\n  4. CONTENT RATINGS")
    print(f"     Category: {m['content_rating']['category']}")
    print(f"     All questionnaire items: No")
    print(f"     Expected rating: {m['content_rating']['expected_rating']}")

    print(f"\n  5. TARGET AUDIENCE")
    print(f"     Age groups: {', '.join(m['target_audience']['age_groups'])}")
    print(f"     Appeals to children: {'Yes' if m['target_audience']['appeals_to_children'] else 'No'}")

    print(f"\n  6. DATA SAFETY")
    print(f"     Data collected: {'Yes' if m['data_safety']['collects_data'] else 'No'}")
    print(f"     Data shared:    {'Yes' if m['data_safety']['shares_data'] else 'No'}")
    print(f"     Encrypted in transit: {'Yes' if m['data_safety']['encrypted_in_transit'] else 'No'}")
    print(f"     Users can request deletion: {'Yes' if m['data_safety']['users_can_request_deletion'] else 'No'}")

    print(f"\n  7. ADVERTISING ID")
    print(f"     Uses advertising ID? -> {'Yes' if m['advertising_id']['uses_advertising_id'] else 'No'}")

    print(f"\n  8. GOVERNMENT APPS")
    print(f"     -> No")

    print(f"\n  9. FINANCIAL FEATURES")
    print(f"     -> No")

    print(f"\n  10. SPECIAL CATEGORIES (news, health, COVID, etc.)")
    print(f"     -> No to all")


def main():
    cfg    = load_config()
    target = sys.argv[1] if len(sys.argv) > 1 else None

    print("\nApp Factory v2 - Play Console 'App Content' Standard Answer Sheet")
    print(f"Source: {CONFIG.relative_to(REPO_ROOT)}")

    for ws, name, slug in APPS:
        if target and ws != target:
            continue
        print_app(cfg, ws, name, slug)

    print(f"\n{'='*68}")
    print("  Done. Open Play Console -> each app -> Policy and programmes")
    print("        -> App content, then fill in each 'Start declaration'")
    print("        section using the values above.")
    print('='*68 + "\n")


if __name__ == "__main__":
    main()
