#!/usr/bin/env python3
"""
App Factory v2 — Patch iOS pbxproj: exclude Info.plist from auto-include
==========================================================================
Xcode 16 introduced PBXFileSystemSynchronizedRootGroup which auto-includes
every file in the source folder as a build resource. That clashes with the
INFOPLIST_FILE setting (the same Info.plist gets treated as both the app's
plist AND a copy-bundle-resources entry) and `gym` crashes with:

    error: duplicate output file '.../Info.plist' on task: ProcessInfoPlistFile

The fix is a PBXFileSystemSynchronizedBuildFileExceptionSet that excludes
Info.plist from auto-include. This script adds it to every iOS .pbxproj
in the workspaces, idempotently.

Run:  python scripts/fix_ios_infoplist_exception.py
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()

# Per-app unique ID suffix for the exception object (must not collide
# with the existing A100000000000000000000{1..C} ids).
EXCEPTION_ID_SUFFIX = "F01"


def patch_pbxproj(pbx_path: Path) -> bool:
    """Returns True if file was changed, False if already patched / no-op."""
    text = pbx_path.read_text(encoding="utf-8")

    if "PBXFileSystemSynchronizedBuildFileExceptionSet" in text:
        return False  # already patched

    if "PBXFileSystemSynchronizedRootGroup" not in text:
        # not a Xcode-16-style project; nothing to do
        return False

    # Find the root-group id and the target id by scanning a few obvious
    # places. xcodebuild IDs are 24-char hex tokens but some templates
    # use shorter / mixed-alnum tokens, so accept any non-space identifier.
    m_root = re.search(
        r"(\S+)\s+/\*\s+[^*]+\*/\s*=\s*\{\s*isa\s*=\s*PBXFileSystemSynchronizedRootGroup;",
        text,
    )
    if not m_root:
        return False
    root_id = m_root.group(1)

    # Find the native target id (the only PBXNativeTarget in the file)
    m_target = re.search(
        r"(\S+)\s+/\*\s+[^*]+\*/\s*=\s*\{\s*isa\s*=\s*PBXNativeTarget;",
        text,
    )
    if not m_target:
        return False
    target_id = m_target.group(1)

    # Build a new unique exception id by replacing the last 3 chars of the
    # root-group id with our suffix.
    exception_id = root_id[:-3] + EXCEPTION_ID_SUFFIX

    # Pick a human label using the project's target name
    m_name = re.search(r"name\s*=\s*([A-Za-z0-9_]+);\s*productName", text)
    target_label = m_name.group(1) if m_name else "App"

    # 1) Add the exceptions array reference to the root group
    new_root_group = (
        "isa = PBXFileSystemSynchronizedRootGroup;\n"
        "\t\t\texceptions = (\n"
        f"\t\t\t\t{exception_id} /* Exceptions for {target_label} */,\n"
        "\t\t\t);\n"
    )
    text = re.sub(
        r"isa\s*=\s*PBXFileSystemSynchronizedRootGroup;\s*",
        new_root_group,
        text,
        count=1,
    )

    # 2) Insert a new PBXFileSystemSynchronizedBuildFileExceptionSet
    #    section just before the PBXFileSystemSynchronizedRootGroup section.
    new_section = (
        f"/* Begin PBXFileSystemSynchronizedBuildFileExceptionSet section */\n"
        f"\t\t{exception_id} /* Exceptions for {target_label} */ = {{\n"
        f"\t\t\tisa = PBXFileSystemSynchronizedBuildFileExceptionSet;\n"
        f"\t\t\tmembershipExceptions = (\n"
        f"\t\t\t\tInfo.plist,\n"
        f"\t\t\t);\n"
        f"\t\t\ttarget = {target_id} /* {target_label} */;\n"
        f"\t\t}};\n"
        f"/* End PBXFileSystemSynchronizedBuildFileExceptionSet section */\n\n"
    )
    text = text.replace(
        "/* Begin PBXFileSystemSynchronizedRootGroup section */",
        new_section + "/* Begin PBXFileSystemSynchronizedRootGroup section */",
        1,
    )

    pbx_path.write_text(text, encoding="utf-8")
    return True


def main():
    pbx_files = sorted(REPO_ROOT.glob("workspaces/*/ios/*.xcodeproj/project.pbxproj"))
    if not pbx_files:
        print("No iOS pbxproj files found.")
        return

    for pbx in pbx_files:
        rel = pbx.relative_to(REPO_ROOT)
        changed = patch_pbxproj(pbx)
        print(f"  {'[patched]' if changed else '[skip]   '}  {rel}")


if __name__ == "__main__":
    main()
