#!/usr/bin/env python3
"""
App Factory v2 — Patch iOS pbxproj: force distribution signing
================================================================
xcodebuild archive defaults to creating an "iOS App Development"
provisioning profile when CODE_SIGN_IDENTITY isn't pinned. Development
profiles require at least one registered device on the team, which a
fresh App-Store-only account doesn't have, so the archive fails with:

    Your team has no devices from which to generate a provisioning profile

The fix is to set CODE_SIGN_IDENTITY = "Apple Distribution" on the
Release configuration so the archive uses an App-Store-Connect-issued
distribution profile (no device registration needed).

This script idempotently injects the identity into every iOS
project.pbxproj under workspaces/.

Run:  python scripts/fix_ios_signing_identity.py
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()


def patch_pbxproj(pbx_path: Path) -> bool:
    text = pbx_path.read_text(encoding="utf-8")
    original = text

    # Find every XCBuildConfiguration whose name is "Release". Inject
    # CODE_SIGN_IDENTITY[sdk=iphoneos*] = "Apple Distribution" into its
    # buildSettings block if not already present.
    #
    # The pattern: a buildSettings { ... } block, followed by name = Release;
    pattern = re.compile(
        r"(buildSettings\s*=\s*\{)([^}]*?)(\};\s*name\s*=\s*Release;)",
        re.DOTALL,
    )

    def insert(match):
        head, body, tail = match.group(1), match.group(2), match.group(3)
        if "CODE_SIGN_IDENTITY" in body:
            return match.group(0)  # already patched
        # Insert after CODE_SIGN_STYLE = Automatic line if present,
        # otherwise just append before the closing brace.
        injection = '\n\t\t\t\tCODE_SIGN_IDENTITY = "Apple Distribution";'
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

    text = pattern.sub(insert, text)

    if text == original:
        return False
    pbx_path.write_text(text, encoding="utf-8")
    return True


def main():
    pbx_files = sorted(REPO_ROOT.glob("workspaces/*/ios/*.xcodeproj/project.pbxproj"))
    for pbx in pbx_files:
        rel = pbx.relative_to(REPO_ROOT)
        changed = patch_pbxproj(pbx)
        print(f"  {'[patched]' if changed else '[skip]   '}  {rel}")


if __name__ == "__main__":
    main()
