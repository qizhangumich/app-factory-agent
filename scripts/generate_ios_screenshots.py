#!/usr/bin/env python3
"""
App Factory v2 — iOS App Store Screenshot Generator
======================================================
Renders each app's existing screen designs at the canonical App Store
Connect screenshot sizes:

  iPhone 6.7" Display  (1290 x 2796)  — required
  iPad Pro 12.9" (6th gen)  (2048 x 2732)  — required if app supports iPad

Reuses the per-app screen builders from generate_app_screenshots.py so
the UI in iOS screenshots is consistent with Android.

Output: workspaces/<ws>/ios/fastlane/screenshots/en-US/<size_key>_N.png

Run:  python scripts/generate_ios_screenshots.py
"""

import asyncio, importlib.util, sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()


def load_app_screenshots_module():
    """Import generate_app_screenshots.py by path (it's a sibling script,
    not a package, so importlib is the cleanest cross-platform approach)."""
    spec = importlib.util.spec_from_file_location(
        "generate_app_screenshots",
        REPO_ROOT / "scripts" / "generate_app_screenshots.py",
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["generate_app_screenshots"] = mod
    spec.loader.exec_module(mod)
    return mod


# App Store Connect screenshot sizes that map 1:1 to a deviceClass display
# type used by the asc_release.py uploader. Width × Height in portrait.
IOS_SIZES = [
    ("iphone_6_7", 1290, 2796),
    ("ipad_12_9",  2048, 2732),
]


def out_dir(ws: str) -> Path:
    p = REPO_ROOT / "workspaces" / ws / "ios" / "fastlane" / "screenshots" / "en-US"
    p.mkdir(parents=True, exist_ok=True)
    return p


async def render(page, html, w, h, out_path):
    await page.set_viewport_size({"width": w, "height": h})
    await page.set_content(html)
    await page.wait_for_timeout(150)
    await page.screenshot(path=str(out_path), type="png",
                          clip={"x": 0, "y": 0, "width": w, "height": h})
    print(f"    {out_path.name}")


async def main():
    from playwright.async_api import async_playwright

    gen = load_app_screenshots_module()

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page    = await browser.new_page()

        for ws, builder in gen.APPS:
            od = out_dir(ws)
            print(f"\n[{ws}]")
            for size_key, w, h in IOS_SIZES:
                screens = builder(w, h)
                for i, html in enumerate(screens, 1):
                    await render(page, html, w, h, od / f"{size_key}_{i}.png")

        await browser.close()
    print("\n[DONE]")


if __name__ == "__main__":
    asyncio.run(main())
