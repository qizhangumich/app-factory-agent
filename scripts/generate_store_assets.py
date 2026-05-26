#!/usr/bin/env python3
"""
App Factory v2 - Store Asset Generator
=======================================
Generates Play Store assets for all apps using Playwright:
  - 512x512 icon PNG  (store/icon.png)
  - 1024x500 feature graphic PNG  (store/feature.png)
  - 3 promo screenshots 1080x1920 PNG  (store/screen_1..3.png)

Output per app: workspaces/<ws>/android/fastlane/metadata/android/en-US/images/

Usage:
    python scripts/generate_store_assets.py
"""

import asyncio, re, textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()

APPS = [
    {
        "workspace": "ws_001_tipcalcdeluxe",
        "name":      "Tip Calculator Deluxe",
        "tagline":   "Split any bill in seconds",
        "color1":    "#0A84FF",
        "color2":    "#005EC4",
        "features":  ["Custom tip & tax", "Split up to 20 people", "Ad-free & offline"],
    },
    {
        "workspace": "ws_002_unitconverterpro",
        "name":      "Unit Converter Pro",
        "tagline":   "50+ unit types, instant results",
        "color1":    "#4F46E5",
        "color2":    "#3730A3",
        "features":  ["Length, weight, temperature", "Currency & more", "Favorites & history"],
    },
    {
        "workspace": "ws_004_qrbarcodescanner",
        "name":      "QR & Barcode Scanner+",
        "tagline":   "Scan anything, instantly",
        "color1":    "#34C759",
        "color2":    "#1E7A34",
        "features":  ["QR codes & all barcodes", "Scan history", "No ads, no sign-up"],
    },
    {
        "workspace": "ws_005_pomodorofocus",
        "name":      "Pomodoro Focus Timer",
        "tagline":   "Deep work, one session at a time",
        "color1":    "#3FB0A8",
        "color2":    "#2A7A74",
        "features":  ["Custom intervals", "Session streaks", "Focus statistics"],
    },
]


def svg_path(ws: str) -> Path:
    return REPO_ROOT / "workspaces" / ws / "shared" / "app_icon.svg"

def out_dir(ws: str) -> Path:
    p = (REPO_ROOT / "workspaces" / ws /
         "android" / "fastlane" / "metadata" / "android" / "en-US" / "images")
    p.mkdir(parents=True, exist_ok=True)
    return p


def icon_html(svg_content: str, color1: str) -> str:
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ width:512px; height:512px; background:linear-gradient(135deg,{color1},{color1}cc);
         display:flex; align-items:center; justify-content:center; border-radius:80px; overflow:hidden; }}
  .icon {{ width:340px; height:340px; }}
</style></head><body>
<div class="icon">{svg_content}</div>
</body></html>"""


def feature_html(svg_content: str, name: str, tagline: str, color1: str, color2: str) -> str:
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ width:1024px; height:500px;
         background:linear-gradient(135deg,{color1} 0%,{color2} 100%);
         display:flex; align-items:center; justify-content:center;
         font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; overflow:hidden; }}
  .wrap {{ display:flex; align-items:center; gap:60px; padding:0 80px; width:100%; }}
  .icon {{ width:180px; height:180px; flex-shrink:0; filter:drop-shadow(0 8px 24px rgba(0,0,0,0.3)); }}
  .text {{ color:#fff; }}
  h1 {{ font-size:42px; font-weight:700; line-height:1.15; margin-bottom:12px;
        text-shadow:0 2px 8px rgba(0,0,0,0.2); }}
  p  {{ font-size:22px; opacity:0.88; font-weight:400; }}
</style></head><body>
<div class="wrap">
  <div class="icon">{svg_content}</div>
  <div class="text">
    <h1>{name}</h1>
    <p>{tagline}</p>
  </div>
</div>
</body></html>"""


def screenshot_html(svg_content: str, name: str, tagline: str,
                    features: list, color1: str, color2: str, screen_num: int) -> str:
    screens = [
        # Screen 1: hero
        f"""
        <div class="phone-content hero">
          <div class="app-icon">{svg_content}</div>
          <h1>{name}</h1>
          <p class="sub">{tagline}</p>
        </div>""",
        # Screen 2: features
        f"""
        <div class="phone-content features">
          <h2>Features</h2>
          {''.join(f'<div class="feat"><span class="dot"></span>{f}</div>' for f in features)}
        </div>""",
        # Screen 3: CTA
        f"""
        <div class="phone-content cta">
          <div class="app-icon small">{svg_content}</div>
          <h1>Free &amp; Offline</h1>
          <p class="sub">No ads. No account.<br>No data collection.</p>
        </div>""",
    ]
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ width:1080px; height:1920px; overflow:hidden;
         background:linear-gradient(160deg,{color1} 0%,{color2} 100%);
         font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; color:#fff; }}
  .phone-content {{ width:100%; height:100%; display:flex; flex-direction:column;
                    align-items:center; justify-content:center; padding:120px 80px; gap:40px; }}
  .app-icon {{ width:280px; height:280px; filter:drop-shadow(0 16px 40px rgba(0,0,0,0.4)); }}
  .app-icon.small {{ width:160px; height:160px; }}
  h1 {{ font-size:88px; font-weight:800; text-align:center; line-height:1.1;
        text-shadow:0 4px 16px rgba(0,0,0,0.3); }}
  h2 {{ font-size:72px; font-weight:700; margin-bottom:20px; }}
  .sub {{ font-size:52px; opacity:0.85; text-align:center; line-height:1.4; }}
  .feat {{ font-size:52px; display:flex; align-items:center; gap:24px; margin:12px 0; opacity:0.92; }}
  .dot {{ width:20px; height:20px; background:#fff; border-radius:50%; flex-shrink:0; opacity:0.7; }}
</style></head><body>
{screens[screen_num - 1]}
</body></html>"""


async def render(page, html: str, width: int, height: int, out_path: Path) -> None:
    await page.set_viewport_size({"width": width, "height": height})
    await page.set_content(html)
    await page.wait_for_timeout(200)
    await page.screenshot(path=str(out_path), type="png",
                          clip={"x": 0, "y": 0, "width": width, "height": height})
    print(f"    Saved: {out_path.name}")


async def generate_all() -> None:
    from playwright.async_api import async_playwright

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page    = await browser.new_page()

        for app in APPS:
            ws      = app["workspace"]
            svg_raw = svg_path(ws).read_text(encoding="utf-8", errors="ignore")
            od      = out_dir(ws)
            print(f"\n[{app['name']}]")

            # 512x512 icon
            await render(page, icon_html(svg_raw, app["color1"]),
                         512, 512, od / "icon.png")

            # 1024x500 feature graphic
            await render(page, feature_html(svg_raw, app["name"], app["tagline"],
                                             app["color1"], app["color2"]),
                         1024, 500, od / "feature.png")

            # 3 screenshots 1080x1920
            for i in range(1, 4):
                await render(page,
                             screenshot_html(svg_raw, app["name"], app["tagline"],
                                             app["features"], app["color1"], app["color2"], i),
                             1080, 1920, od / f"screen_{i}.png")

        await browser.close()

    print("\n[DONE] All store assets generated.")


if __name__ == "__main__":
    asyncio.run(generate_all())
