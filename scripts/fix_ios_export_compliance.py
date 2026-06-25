#!/usr/bin/env python3
"""
App Factory v2 — Patch iOS Info.plist for Export Compliance auto-answer
=========================================================================
Every TestFlight build on App Store Connect normally prompts:
  "Does your app use encryption?"
because of US export law. For utility apps that use only Apple's standard
HTTPS / Keychain (no custom crypto), the answer is "exempt." Setting
  ITSAppUsesNonExemptEncryption = NO
in Info.plist tells Apple "yes I've answered, the answer is exempt"
and skips the prompt forever — including for all future builds.

Idempotent: re-runs are safe; if the key already exists, the file isn't
modified.

Run:  python scripts/fix_ios_export_compliance.py
"""

from pathlib import Path
import re

REPO_ROOT = Path(__file__).parent.parent.resolve()


def patch_plist(plist_path: Path) -> bool:
    text = plist_path.read_text(encoding="utf-8")
    if "ITSAppUsesNonExemptEncryption" in text:
        return False
    # Insert before </dict>\n</plist>. We use a simple anchor at the
    # last </dict> on the assumption that the file is well-formed Apple
    # XML (which it is, since Xcode generated it).
    insertion = (
        "\t<key>ITSAppUsesNonExemptEncryption</key>\n"
        "\t<false/>\n"
    )
    if "</dict>\n</plist>" not in text:
        # Tolerate trailing whitespace differences
        m = re.search(r"</dict>\s*</plist>\s*$", text)
        if not m:
            return False
        text = text[:m.start()] + insertion + text[m.start():]
    else:
        text = text.replace(
            "</dict>\n</plist>",
            insertion + "</dict>\n</plist>",
            1,
        )
    plist_path.write_text(text, encoding="utf-8")
    return True


def main():
    plists = sorted(REPO_ROOT.glob("workspaces/*/ios/*/Info.plist"))
    for p in plists:
        rel = p.relative_to(REPO_ROOT)
        changed = patch_plist(p)
        print(f"  {'[patched]' if changed else '[skip]   '}  {rel}")


if __name__ == "__main__":
    main()
