#!/usr/bin/env python3
"""
App Factory v2 — Patch iOS pbxproj for CI distribution signing
================================================================
For Xcode 26 + xcodebuild archive + ASC API-key automatic signing:

The combination that works is:
  - CODE_SIGN_STYLE = Automatic           (let Xcode manage profiles)
  - DEVELOPMENT_TEAM = <team id>          (baked into project, not via xcargs;
                                           Automatic signing needs it set
                                           at project scope, not as override)
  - DO NOT set CODE_SIGN_IDENTITY         (conflicts with Automatic)
  - -allowProvisioningUpdates             (in xcargs)
  - -authenticationKeyPath / ID / IssuerID (in xcargs)

Earlier I tried setting CODE_SIGN_IDENTITY = "Apple Distribution",
which causes Xcode to reject the Automatic signing flow with:
  "automatically signed for development, but a conflicting code signing
   identity Apple Distribution has been manually specified"

So this script undoes that bad override and instead bakes the team id
into the Release config. The team id is not sensitive (visible to anyone
who runs the App Store app on a device).

Run:  python scripts/fix_ios_signing_identity.py
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
TEAM_ID   = "FNGC54MTDA"   # LINKWAVE PTE.LTD. Apple Developer team id


def patch_pbxproj(pbx_path: Path) -> bool:
    text = pbx_path.read_text(encoding="utf-8")
    original = text

    # Step 1: remove the bad CODE_SIGN_IDENTITY = "Apple Distribution" line.
    text = re.sub(
        r'\n\s*CODE_SIGN_IDENTITY\s*=\s*"Apple Distribution"\s*;',
        "",
        text,
    )

    # Step 2: add DEVELOPMENT_TEAM = <team> to both Debug and Release
    # configurations (if not already present). We insert it after the
    # CODE_SIGN_STYLE line.
    def insert_team(match):
        head, body, tail = match.group(1), match.group(2), match.group(3)
        if "DEVELOPMENT_TEAM" in body:
            return match.group(0)
        injection = f'\n\t\t\t\tDEVELOPMENT_TEAM = {TEAM_ID};'
        if "CODE_SIGN_STYLE" in body:
            body = re.sub(
                r"(CODE_SIGN_STYLE\s*=\s*[A-Za-z]+\s*;)",
                r"\1" + injection,
                body,
                count=1,
            )
        else:
            body = body.rstrip() + injection + "\n\t\t\t"
        return head + body + tail

    pattern = re.compile(
        r"(buildSettings\s*=\s*\{)([^}]*?)(\};\s*name\s*=\s*(?:Debug|Release);)",
        re.DOTALL,
    )
    text = pattern.sub(insert_team, text)

    if text == original:
        return False
    pbx_path.write_text(text, encoding="utf-8")
    return True


def main():
    for pbx in sorted(REPO_ROOT.glob("workspaces/*/ios/*.xcodeproj/project.pbxproj")):
        rel = pbx.relative_to(REPO_ROOT)
        changed = patch_pbxproj(pbx)
        print(f"  {'[patched]' if changed else '[skip]   '}  {rel}")


if __name__ == "__main__":
    main()
