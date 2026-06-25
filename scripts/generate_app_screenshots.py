#!/usr/bin/env python3
"""
App Factory v2 — Realistic App Screenshot Generator
=====================================================
Renders authentic-looking Android UI screenshots for each app, NOT marketing
graphics. Google Play rejects promo-style screenshots under the Metadata
Policy ("App screenshot doesn't describe the core functionality"); these
screenshots show what users will actually see when they open the app.

For each app we render 3 phone (1080x1920) + 3 seven-inch (1200x1920) +
3 ten-inch (1600x2560) PNGs into the app's fastlane metadata folder.

Run:  python scripts/generate_app_screenshots.py
"""

import asyncio
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()


def images_dir(ws: str) -> Path:
    p = (REPO_ROOT / "workspaces" / ws /
         "android" / "fastlane" / "metadata" / "android" / "en-US" / "images")
    p.mkdir(parents=True, exist_ok=True)
    return p


# ── Android UI chrome shared across all apps ────────────────────────────────
ANDROID_CHROME_CSS = """
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         -webkit-font-smoothing: antialiased; }
  .phone {
    width: 100%; height: 100%; background: var(--bg, #ffffff); color: var(--fg, #1c1b1f);
    display: flex; flex-direction: column; position: relative; overflow: hidden;
  }
  .statusbar {
    height: 50px; background: var(--bar, var(--bg)); color: var(--fg);
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 32px; font-size: 22px; font-weight: 500;
  }
  .statusbar .right { display: flex; align-items: center; gap: 10px; }
  .topbar {
    padding: 24px 32px 16px; display: flex; align-items: center; gap: 18px;
    background: var(--bar, var(--bg));
  }
  .topbar h1 { font-size: 36px; font-weight: 500; color: var(--fg); }
  .content { flex: 1; padding: 24px 32px; overflow: hidden; }
  .navbar {
    height: 80px; background: var(--bar, var(--bg)); display: flex;
    align-items: center; justify-content: center; gap: 80px;
    border-top: 1px solid rgba(0,0,0,0.08);
  }
  .navbar .nav { display: flex; flex-direction: column; align-items: center;
                 gap: 4px; opacity: 0.65; font-size: 18px; }
  .navbar .nav.active { opacity: 1; color: var(--accent); }
  .navbar .nav .ico { width: 32px; height: 32px; border-radius: 50%;
                       background: currentColor; opacity: 0.85; }
  .card { background: var(--card, #f7f4ef); border-radius: 24px; padding: 28px; }
  button { font-family: inherit; }
"""


def page(viewport_w: int, viewport_h: int, css_vars: str, body_html: str) -> str:
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
{ANDROID_CHROME_CSS}
body {{ width: {viewport_w}px; height: {viewport_h}px; {css_vars} }}
</style></head><body>{body_html}</body></html>"""


def with_chrome(viewport_w: int, viewport_h: int, app_title: str, css_vars: str,
                content_html: str, nav_items: list, active_nav: str) -> str:
    nav_html = "".join(
        f'<div class="nav {"active" if n == active_nav else ""}">'
        f'<div class="ico"></div><span>{n}</span></div>'
        for n in nav_items
    )
    body = f"""
    <div class="phone">
      <div class="statusbar">
        <span>9:41</span>
        <div class="right"><span>5G</span><span>100%</span></div>
      </div>
      <div class="topbar"><h1>{app_title}</h1></div>
      <div class="content">{content_html}</div>
      <div class="navbar">{nav_html}</div>
    </div>"""
    return page(viewport_w, viewport_h, css_vars, body)


# ── Per-app screen designs ──────────────────────────────────────────────────

def tipcalc_screens(w, h):
    base = ":root { --bg:#FAFAFB; --fg:#1c1b1f; --bar:#FAFAFB; --accent:#0A84FF; --card:#F2F4F8; }"
    s1 = with_chrome(w, h, "Tip Calculator Deluxe", base, """
      <div class="card" style="margin-bottom:20px;">
        <div style="font-size:22px;opacity:0.65;margin-bottom:8px;">Bill amount</div>
        <div style="font-size:72px;font-weight:600;color:#0A84FF;">$84.50</div>
      </div>
      <div class="card" style="margin-bottom:20px;">
        <div style="display:flex;justify-content:space-between;margin-bottom:12px;">
          <span style="font-size:24px;">Tip</span>
          <span style="font-size:24px;font-weight:600;color:#0A84FF;">18%</span>
        </div>
        <div style="height:6px;background:#E0E4EC;border-radius:3px;position:relative;">
          <div style="position:absolute;left:0;top:0;height:100%;width:36%;background:#0A84FF;border-radius:3px;"></div>
          <div style="position:absolute;left:36%;top:-7px;width:20px;height:20px;background:#0A84FF;border-radius:50%;box-shadow:0 2px 6px rgba(10,132,255,0.4);"></div>
        </div>
        <div style="display:flex;gap:12px;margin-top:20px;">
          <div style="flex:1;padding:14px 0;text-align:center;border-radius:14px;background:#E8EAF1;font-size:22px;">15%</div>
          <div style="flex:1;padding:14px 0;text-align:center;border-radius:14px;background:#0A84FF;color:#fff;font-size:22px;font-weight:600;">18%</div>
          <div style="flex:1;padding:14px 0;text-align:center;border-radius:14px;background:#E8EAF1;font-size:22px;">20%</div>
          <div style="flex:1;padding:14px 0;text-align:center;border-radius:14px;background:#E8EAF1;font-size:22px;">25%</div>
        </div>
      </div>
      <div class="card" style="margin-bottom:20px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span style="font-size:24px;">Split between</span>
          <div style="display:flex;align-items:center;gap:24px;">
            <div style="width:48px;height:48px;border:2px solid #0A84FF;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#0A84FF;font-size:32px;">-</div>
            <span style="font-size:36px;font-weight:600;color:#0A84FF;">4</span>
            <div style="width:48px;height:48px;border:2px solid #0A84FF;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#0A84FF;font-size:32px;">+</div>
          </div>
        </div>
      </div>
      <div class="card" style="background:linear-gradient(135deg,#0A84FF,#0066CC);color:white;">
        <div style="font-size:22px;opacity:0.85;margin-bottom:8px;">Per person</div>
        <div style="font-size:72px;font-weight:700;">$24.93</div>
        <div style="font-size:20px;opacity:0.85;margin-top:8px;">Total $99.71  ·  Tip $15.21</div>
      </div>
    """, ["Calculator", "History", "Settings"], "Calculator")

    s2 = with_chrome(w, h, "Per-person breakdown", base, """
      <div class="card" style="margin-bottom:16px;display:flex;justify-content:space-between;align-items:center;">
        <div>
          <div style="font-size:24px;">Person 1</div>
          <div style="font-size:18px;opacity:0.6;">Subtotal $21.13 · Tip $3.80</div>
        </div>
        <div style="font-size:32px;font-weight:600;color:#0A84FF;">$24.93</div>
      </div>
      <div class="card" style="margin-bottom:16px;display:flex;justify-content:space-between;align-items:center;">
        <div>
          <div style="font-size:24px;">Person 2</div>
          <div style="font-size:18px;opacity:0.6;">Subtotal $21.13 · Tip $3.80</div>
        </div>
        <div style="font-size:32px;font-weight:600;color:#0A84FF;">$24.93</div>
      </div>
      <div class="card" style="margin-bottom:16px;display:flex;justify-content:space-between;align-items:center;">
        <div>
          <div style="font-size:24px;">Person 3</div>
          <div style="font-size:18px;opacity:0.6;">Subtotal $21.13 · Tip $3.80</div>
        </div>
        <div style="font-size:32px;font-weight:600;color:#0A84FF;">$24.93</div>
      </div>
      <div class="card" style="margin-bottom:16px;display:flex;justify-content:space-between;align-items:center;">
        <div>
          <div style="font-size:24px;">Person 4</div>
          <div style="font-size:18px;opacity:0.6;">Subtotal $21.11 · Tip $3.81</div>
        </div>
        <div style="font-size:32px;font-weight:600;color:#0A84FF;">$24.92</div>
      </div>
      <div style="margin-top:32px;padding:28px;background:#F2F4F8;border-radius:24px;">
        <div style="display:flex;justify-content:space-between;font-size:22px;margin-bottom:8px;">
          <span>Subtotal</span><span>$84.50</span>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:22px;margin-bottom:8px;">
          <span>Tax 8%</span><span>$6.76</span>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:22px;margin-bottom:16px;">
          <span>Tip 18%</span><span>$15.21</span>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:30px;font-weight:600;color:#0A84FF;border-top:1px solid #E0E4EC;padding-top:16px;">
          <span>Total</span><span>$106.47</span>
        </div>
      </div>
    """, ["Calculator", "History", "Settings"], "Calculator")

    s3 = with_chrome(w, h, "History", base, """
      <div class="card" style="margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <div>
            <div style="font-size:22px;font-weight:500;">Dinner with friends</div>
            <div style="font-size:18px;opacity:0.6;margin-top:4px;">Today · 8:42 PM · split 4 ways</div>
          </div>
          <div style="text-align:right;">
            <div style="font-size:26px;font-weight:600;color:#0A84FF;">$106.47</div>
            <div style="font-size:18px;opacity:0.6;">18% tip</div>
          </div>
        </div>
      </div>
      <div class="card" style="margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <div>
            <div style="font-size:22px;font-weight:500;">Lunch meeting</div>
            <div style="font-size:18px;opacity:0.6;margin-top:4px;">Today · 12:18 PM · split 2 ways</div>
          </div>
          <div style="text-align:right;">
            <div style="font-size:26px;font-weight:600;color:#0A84FF;">$52.30</div>
            <div style="font-size:18px;opacity:0.6;">20% tip</div>
          </div>
        </div>
      </div>
      <div class="card" style="margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <div>
            <div style="font-size:22px;font-weight:500;">Coffee run</div>
            <div style="font-size:18px;opacity:0.6;margin-top:4px;">Yesterday · 9:14 AM · 1 person</div>
          </div>
          <div style="text-align:right;">
            <div style="font-size:26px;font-weight:600;color:#0A84FF;">$8.40</div>
            <div style="font-size:18px;opacity:0.6;">15% tip</div>
          </div>
        </div>
      </div>
      <div class="card" style="margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <div>
            <div style="font-size:22px;font-weight:500;">Pizza night</div>
            <div style="font-size:18px;opacity:0.6;margin-top:4px;">Saturday · 7:32 PM · split 5 ways</div>
          </div>
          <div style="text-align:right;">
            <div style="font-size:26px;font-weight:600;color:#0A84FF;">$74.20</div>
            <div style="font-size:18px;opacity:0.6;">18% tip</div>
          </div>
        </div>
      </div>
      <div class="card" style="margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <div>
            <div style="font-size:22px;font-weight:500;">Brunch</div>
            <div style="font-size:18px;opacity:0.6;margin-top:4px;">Saturday · 11:08 AM · split 3 ways</div>
          </div>
          <div style="text-align:right;">
            <div style="font-size:26px;font-weight:600;color:#0A84FF;">$48.60</div>
            <div style="font-size:18px;opacity:0.6;">20% tip</div>
          </div>
        </div>
      </div>
    """, ["Calculator", "History", "Settings"], "History")
    return [s1, s2, s3]


def unitconv_screens(w, h):
    base = ":root { --bg:#FAFAFB; --fg:#1c1b1f; --bar:#FAFAFB; --accent:#4F46E5; --card:#F2F0FA; }"
    s1 = with_chrome(w, h, "Length", base, """
      <div style="padding:20px 0 32px;text-align:center;">
        <div style="display:inline-flex;background:#E8E5F7;padding:6px;border-radius:14px;font-size:20px;">
          <span style="padding:10px 22px;background:#4F46E5;color:white;border-radius:10px;">Length</span>
          <span style="padding:10px 22px;opacity:0.6;">Weight</span>
          <span style="padding:10px 22px;opacity:0.6;">Volume</span>
        </div>
      </div>
      <div class="card" style="background:linear-gradient(135deg,#4F46E5,#3730A3);color:white;margin-bottom:24px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
          <span style="font-size:22px;opacity:0.85;">From</span>
          <span style="font-size:24px;font-weight:600;">Meters</span>
        </div>
        <div style="font-size:78px;font-weight:600;line-height:1;">1.85</div>
      </div>
      <div style="display:flex;justify-content:center;margin:-12px 0 -12px;">
        <div style="width:56px;height:56px;background:#4F46E5;border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-size:28px;box-shadow:0 4px 16px rgba(79,70,229,0.35);">⇅</div>
      </div>
      <div class="card" style="margin-bottom:24px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
          <span style="font-size:22px;opacity:0.65;">To</span>
          <span style="font-size:24px;font-weight:600;color:#4F46E5;">Feet</span>
        </div>
        <div style="font-size:78px;font-weight:600;line-height:1;color:#4F46E5;">6.0696</div>
      </div>
      <div style="margin-top:16px;font-size:22px;opacity:0.65;">Related conversions</div>
      <div style="display:flex;gap:12px;margin-top:16px;flex-wrap:wrap;">
        <div style="padding:14px 22px;background:#E8E5F7;border-radius:16px;font-size:20px;">1.85 m = 72.835 in</div>
        <div style="padding:14px 22px;background:#E8E5F7;border-radius:16px;font-size:20px;">1.85 m = 185 cm</div>
      </div>
    """, ["Convert", "Favorites", "History"], "Convert")

    s2 = with_chrome(w, h, "Categories", base, """
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
        <div class="card" style="background:linear-gradient(135deg,#4F46E5,#7C3AED);color:white;padding:32px 24px;">
          <div style="font-size:42px;margin-bottom:12px;">⟷</div>
          <div style="font-size:26px;font-weight:600;">Length</div>
          <div style="font-size:18px;opacity:0.85;margin-top:4px;">m, ft, in, km, mi…</div>
        </div>
        <div class="card" style="padding:32px 24px;">
          <div style="font-size:42px;margin-bottom:12px;color:#4F46E5;">⚖</div>
          <div style="font-size:26px;font-weight:600;">Weight</div>
          <div style="font-size:18px;opacity:0.65;margin-top:4px;">kg, lb, oz, g…</div>
        </div>
        <div class="card" style="padding:32px 24px;">
          <div style="font-size:42px;margin-bottom:12px;color:#4F46E5;">🌡</div>
          <div style="font-size:26px;font-weight:600;">Temperature</div>
          <div style="font-size:18px;opacity:0.65;margin-top:4px;">°C, °F, K</div>
        </div>
        <div class="card" style="padding:32px 24px;">
          <div style="font-size:42px;margin-bottom:12px;color:#4F46E5;">⏱</div>
          <div style="font-size:26px;font-weight:600;">Speed</div>
          <div style="font-size:18px;opacity:0.65;margin-top:4px;">km/h, mph, m/s…</div>
        </div>
        <div class="card" style="padding:32px 24px;">
          <div style="font-size:42px;margin-bottom:12px;color:#4F46E5;">▢</div>
          <div style="font-size:26px;font-weight:600;">Area</div>
          <div style="font-size:18px;opacity:0.65;margin-top:4px;">m², ft², acre…</div>
        </div>
        <div class="card" style="padding:32px 24px;">
          <div style="font-size:42px;margin-bottom:12px;color:#4F46E5;">▣</div>
          <div style="font-size:26px;font-weight:600;">Volume</div>
          <div style="font-size:18px;opacity:0.65;margin-top:4px;">L, gal, oz, mL…</div>
        </div>
        <div class="card" style="padding:32px 24px;">
          <div style="font-size:42px;margin-bottom:12px;color:#4F46E5;">⌛</div>
          <div style="font-size:26px;font-weight:600;">Time</div>
          <div style="font-size:18px;opacity:0.65;margin-top:4px;">s, min, hr, day…</div>
        </div>
        <div class="card" style="padding:32px 24px;">
          <div style="font-size:42px;margin-bottom:12px;color:#4F46E5;">📐</div>
          <div style="font-size:26px;font-weight:600;">Angle</div>
          <div style="font-size:18px;opacity:0.65;margin-top:4px;">deg, rad, grad</div>
        </div>
      </div>
    """, ["Convert", "Favorites", "History"], "Convert")

    s3 = with_chrome(w, h, "Favorites", base, """
      <div class="card" style="margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <div>
            <div style="font-size:22px;font-weight:500;">Meters → Feet</div>
            <div style="font-size:18px;opacity:0.6;margin-top:4px;">Length</div>
          </div>
          <div style="color:#FFD60A;font-size:32px;">★</div>
        </div>
      </div>
      <div class="card" style="margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <div>
            <div style="font-size:22px;font-weight:500;">Celsius → Fahrenheit</div>
            <div style="font-size:18px;opacity:0.6;margin-top:4px;">Temperature</div>
          </div>
          <div style="color:#FFD60A;font-size:32px;">★</div>
        </div>
      </div>
      <div class="card" style="margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <div>
            <div style="font-size:22px;font-weight:500;">Kilograms → Pounds</div>
            <div style="font-size:18px;opacity:0.6;margin-top:4px;">Weight</div>
          </div>
          <div style="color:#FFD60A;font-size:32px;">★</div>
        </div>
      </div>
      <div class="card" style="margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <div>
            <div style="font-size:22px;font-weight:500;">Miles → Kilometers</div>
            <div style="font-size:18px;opacity:0.6;margin-top:4px;">Length</div>
          </div>
          <div style="color:#FFD60A;font-size:32px;">★</div>
        </div>
      </div>
      <div class="card" style="margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <div>
            <div style="font-size:22px;font-weight:500;">Cups → Milliliters</div>
            <div style="font-size:18px;opacity:0.6;margin-top:4px;">Volume (cooking)</div>
          </div>
          <div style="color:#FFD60A;font-size:32px;">★</div>
        </div>
      </div>
      <div class="card" style="margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <div>
            <div style="font-size:22px;font-weight:500;">GB → MB</div>
            <div style="font-size:18px;opacity:0.6;margin-top:4px;">Data storage</div>
          </div>
          <div style="color:#FFD60A;font-size:32px;">★</div>
        </div>
      </div>
    """, ["Convert", "Favorites", "History"], "Favorites")
    return [s1, s2, s3]


def qr_screens(w, h):
    base = ":root { --bg:#0F1A14; --fg:#FFFFFF; --bar:#0F1A14; --accent:#34C759; --card:#1A2820; }"
    s1 = with_chrome(w, h, "Scan", base, """
      <div style="position:relative;width:100%;height:100%;background:linear-gradient(180deg,#1A2820,#0F1A14);border-radius:24px;overflow:hidden;">
        <div style="position:absolute;inset:0;background:radial-gradient(ellipse at center,rgba(52,199,89,0.18) 0%,transparent 60%);"></div>
        <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:600px;height:600px;">
          <div style="position:absolute;inset:0;border:4px solid #34C759;border-radius:32px;
                      mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);mask-composite:exclude;
                      box-shadow:0 0 40px rgba(52,199,89,0.4),inset 0 0 40px rgba(52,199,89,0.2);"></div>
          <div style="position:absolute;top:30px;left:30px;width:80px;height:80px;border-top:6px solid #34C759;border-left:6px solid #34C759;border-radius:8px 0 0 0;"></div>
          <div style="position:absolute;top:30px;right:30px;width:80px;height:80px;border-top:6px solid #34C759;border-right:6px solid #34C759;border-radius:0 8px 0 0;"></div>
          <div style="position:absolute;bottom:30px;left:30px;width:80px;height:80px;border-bottom:6px solid #34C759;border-left:6px solid #34C759;border-radius:0 0 0 8px;"></div>
          <div style="position:absolute;bottom:30px;right:30px;width:80px;height:80px;border-bottom:6px solid #34C759;border-right:6px solid #34C759;border-radius:0 0 8px 0;"></div>
          <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:240px;height:240px;background:white;border-radius:12px;padding:16px;"></div>
          <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:200px;height:200px;
            background:repeating-conic-gradient(#000 0% 3.125%, #fff 0% 6.25%, #000 0% 9.375%, #fff 0% 12.5%);
            background-size:30px 30px;border-radius:4px;"></div>
        </div>
        <div style="position:absolute;bottom:60px;left:50%;transform:translateX(-50%);
                    padding:18px 36px;background:rgba(52,199,89,0.15);border:1.5px solid #34C759;
                    border-radius:30px;color:#34C759;font-size:24px;font-weight:500;">
          Hold steady — scanning
        </div>
        <div style="position:absolute;top:30px;right:30px;display:flex;gap:16px;">
          <div style="width:64px;height:64px;background:rgba(255,255,255,0.15);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:28px;">⚡</div>
          <div style="width:64px;height:64px;background:rgba(255,255,255,0.15);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:28px;">⟲</div>
        </div>
      </div>
    """, ["Scan", "History", "Settings"], "Scan")

    s2 = with_chrome(w, h, "Scan result", ":root { --bg:#FAFAFB; --fg:#1c1b1f; --bar:#FAFAFB; --accent:#34C759; --card:#F0F8F4; }", """
      <div style="text-align:center;padding:40px 0 32px;">
        <div style="width:160px;height:160px;margin:0 auto;background:white;border-radius:24px;padding:18px;
                    box-shadow:0 8px 24px rgba(0,0,0,0.08);">
          <div style="width:100%;height:100%;background:repeating-conic-gradient(#000 0% 3.125%, #fff 0% 6.25%, #000 0% 9.375%, #fff 0% 12.5%);
                      background-size:24px 24px;border-radius:8px;"></div>
        </div>
        <div style="margin-top:24px;color:#34C759;font-size:22px;font-weight:500;">✓ QR code detected</div>
      </div>
      <div class="card" style="margin-bottom:20px;">
        <div style="font-size:18px;opacity:0.6;margin-bottom:8px;">Type</div>
        <div style="font-size:26px;font-weight:500;">URL</div>
      </div>
      <div class="card" style="margin-bottom:20px;">
        <div style="font-size:18px;opacity:0.6;margin-bottom:8px;">Decoded content</div>
        <div style="font-size:26px;color:#0A84FF;word-break:break-all;">https://en.wikipedia.org/wiki/QR_code</div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:32px;">
        <div style="padding:24px;background:#34C759;color:white;border-radius:20px;text-align:center;font-size:24px;font-weight:600;">Open</div>
        <div style="padding:24px;background:#F0F8F4;color:#34C759;border-radius:20px;text-align:center;font-size:24px;font-weight:600;border:2px solid #34C759;">Copy</div>
        <div style="padding:24px;background:#F0F8F4;color:#1c1b1f;border-radius:20px;text-align:center;font-size:24px;font-weight:500;">Share</div>
        <div style="padding:24px;background:#F0F8F4;color:#1c1b1f;border-radius:20px;text-align:center;font-size:24px;font-weight:500;">Save</div>
      </div>
    """, ["Scan", "History", "Settings"], "Scan")

    s3 = with_chrome(w, h, "History", ":root { --bg:#FAFAFB; --fg:#1c1b1f; --bar:#FAFAFB; --accent:#34C759; --card:#F0F8F4; }", """
      <div class="card" style="margin-bottom:16px;">
        <div style="display:flex;gap:20px;align-items:center;">
          <div style="width:72px;height:72px;background:white;border-radius:12px;padding:8px;">
            <div style="width:100%;height:100%;background:repeating-conic-gradient(#000 0% 3.125%, #fff 0% 6.25%, #000 0% 9.375%, #fff 0% 12.5%);background-size:12px 12px;"></div>
          </div>
          <div style="flex:1;">
            <div style="font-size:18px;opacity:0.6;">URL · 2 min ago</div>
            <div style="font-size:22px;color:#0A84FF;">https://en.wikipedia.org/...</div>
          </div>
        </div>
      </div>
      <div class="card" style="margin-bottom:16px;">
        <div style="display:flex;gap:20px;align-items:center;">
          <div style="width:72px;height:72px;background:white;border-radius:12px;padding:8px;display:flex;align-items:center;justify-content:center;">
            <div style="width:100%;height:24px;background:repeating-linear-gradient(90deg,#000 0px,#000 4px,#fff 4px,#fff 7px,#000 7px,#000 10px,#fff 10px,#fff 13px);"></div>
          </div>
          <div style="flex:1;">
            <div style="font-size:18px;opacity:0.6;">Barcode (EAN-13) · 1 h ago</div>
            <div style="font-size:22px;">5901234123457</div>
          </div>
        </div>
      </div>
      <div class="card" style="margin-bottom:16px;">
        <div style="display:flex;gap:20px;align-items:center;">
          <div style="width:72px;height:72px;background:white;border-radius:12px;padding:8px;">
            <div style="width:100%;height:100%;background:repeating-conic-gradient(#000 0% 3.125%, #fff 0% 6.25%, #000 0% 9.375%, #fff 0% 12.5%);background-size:12px 12px;"></div>
          </div>
          <div style="flex:1;">
            <div style="font-size:18px;opacity:0.6;">Wi-Fi · Yesterday</div>
            <div style="font-size:22px;">CoffeeShop_Guest</div>
          </div>
        </div>
      </div>
      <div class="card" style="margin-bottom:16px;">
        <div style="display:flex;gap:20px;align-items:center;">
          <div style="width:72px;height:72px;background:white;border-radius:12px;padding:8px;">
            <div style="width:100%;height:100%;background:repeating-conic-gradient(#000 0% 3.125%, #fff 0% 6.25%, #000 0% 9.375%, #fff 0% 12.5%);background-size:12px 12px;"></div>
          </div>
          <div style="flex:1;">
            <div style="font-size:18px;opacity:0.6;">Text · Yesterday</div>
            <div style="font-size:22px;">Meeting room 4B, 2:30 PM</div>
          </div>
        </div>
      </div>
      <div class="card" style="margin-bottom:16px;">
        <div style="display:flex;gap:20px;align-items:center;">
          <div style="width:72px;height:72px;background:white;border-radius:12px;padding:8px;display:flex;align-items:center;justify-content:center;">
            <div style="width:100%;height:24px;background:repeating-linear-gradient(90deg,#000 0px,#000 5px,#fff 5px,#fff 8px,#000 8px,#000 12px);"></div>
          </div>
          <div style="flex:1;">
            <div style="font-size:18px;opacity:0.6;">Barcode (UPC-A) · 2 days ago</div>
            <div style="font-size:22px;">036000291452</div>
          </div>
        </div>
      </div>
    """, ["Scan", "History", "Settings"], "History")
    return [s1, s2, s3]


def pomodoro_screens(w, h):
    base = ":root { --bg:#0E1614; --fg:#FFFFFF; --bar:#0E1614; --accent:#3FB0A8; --card:#162420; }"
    # Build SVG circular progress
    def ring(percent):
        circumference = 2 * 3.14159 * 280
        offset = circumference * (1 - percent / 100)
        return f"""
        <svg viewBox="0 0 640 640" style="width:100%;height:100%;">
          <circle cx="320" cy="320" r="280" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="20"/>
          <circle cx="320" cy="320" r="280" fill="none" stroke="#3FB0A8" stroke-width="20"
                  stroke-dasharray="{circumference:.1f}" stroke-dashoffset="{offset:.1f}"
                  stroke-linecap="round" transform="rotate(-90 320 320)"
                  style="filter:drop-shadow(0 0 16px rgba(63,176,168,0.55));"/>
        </svg>
        """

    s1 = with_chrome(w, h, "Pomodoro Focus", base, f"""
      <div style="position:relative;width:640px;height:640px;margin:60px auto 32px;">
        {ring(64)}
        <div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;">
          <div style="font-size:24px;color:#3FB0A8;letter-spacing:4px;margin-bottom:16px;">FOCUS · SESSION 3 / 4</div>
          <div style="font-size:130px;font-weight:300;letter-spacing:-2px;line-height:1;">17:42</div>
          <div style="font-size:24px;opacity:0.5;margin-top:24px;">7m 18s elapsed</div>
        </div>
      </div>
      <div style="display:flex;gap:14px;justify-content:center;margin-bottom:32px;">
        <div style="width:18px;height:18px;border-radius:50%;background:#3FB0A8;"></div>
        <div style="width:18px;height:18px;border-radius:50%;background:#3FB0A8;"></div>
        <div style="width:18px;height:18px;border-radius:50%;background:#3FB0A8;border:3px solid rgba(63,176,168,0.4);"></div>
        <div style="width:18px;height:18px;border-radius:50%;background:rgba(255,255,255,0.18);"></div>
      </div>
      <div style="display:flex;gap:16px;justify-content:center;">
        <div style="width:96px;height:96px;background:rgba(255,255,255,0.08);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:28px;">⏯</div>
        <div style="width:96px;height:96px;background:#3FB0A8;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:40px;color:white;">⏸</div>
        <div style="width:96px;height:96px;background:rgba(255,255,255,0.08);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:28px;">⏭</div>
      </div>
    """, ["Timer", "Stats", "Settings"], "Timer")

    # 90-day heat map
    days = []
    intensities = [0,1,2,3,2,1,0,2,3,4,3,2,1,2,3,4,4,3,2,3,4,2,1,0,2,3,4,4,3,2,
                   1,2,3,4,3,2,1,0,2,3,4,4,3,2,1,2,3,4,3,2,3,4,4,3,2,3,4,4,3,2,
                   1,2,3,4,4,3,2,3,4,4,3,2,1,2,3,4,4,3,2,3,4,4,3,2,3,4,4,3]
    colors = ["rgba(255,255,255,0.06)", "rgba(63,176,168,0.25)", "rgba(63,176,168,0.45)",
              "rgba(63,176,168,0.7)", "#3FB0A8"]
    for i, lvl in enumerate(intensities):
        days.append(f'<div style="aspect-ratio:1;background:{colors[lvl]};border-radius:6px;"></div>')
    heatmap = ''.join(days)
    s2 = with_chrome(w, h, "Statistics", base, f"""
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:24px;">
        <div class="card">
          <div style="font-size:18px;opacity:0.6;margin-bottom:8px;">Today</div>
          <div style="font-size:48px;font-weight:600;color:#3FB0A8;">5</div>
          <div style="font-size:18px;opacity:0.6;">sessions · 2h 5m</div>
        </div>
        <div class="card">
          <div style="font-size:18px;opacity:0.6;margin-bottom:8px;">This week</div>
          <div style="font-size:48px;font-weight:600;color:#3FB0A8;">28</div>
          <div style="font-size:18px;opacity:0.6;">sessions · 11h 40m</div>
        </div>
        <div class="card">
          <div style="font-size:18px;opacity:0.6;margin-bottom:8px;">Streak</div>
          <div style="font-size:48px;font-weight:600;color:#3FB0A8;">12 d</div>
          <div style="font-size:18px;opacity:0.6;">current</div>
        </div>
        <div class="card">
          <div style="font-size:18px;opacity:0.6;margin-bottom:8px;">All time</div>
          <div style="font-size:48px;font-weight:600;color:#3FB0A8;">142h</div>
          <div style="font-size:18px;opacity:0.6;">340 sessions</div>
        </div>
      </div>
      <div class="card">
        <div style="font-size:22px;font-weight:500;margin-bottom:8px;">Last 90 days</div>
        <div style="font-size:18px;opacity:0.6;margin-bottom:16px;">Each square is one day</div>
        <div style="display:grid;grid-template-columns:repeat(15,1fr);gap:6px;">{heatmap}</div>
        <div style="display:flex;justify-content:flex-end;align-items:center;gap:8px;font-size:16px;opacity:0.6;margin-top:14px;">
          <span>Less</span>
          <div style="width:14px;height:14px;background:rgba(255,255,255,0.06);border-radius:3px;"></div>
          <div style="width:14px;height:14px;background:rgba(63,176,168,0.25);border-radius:3px;"></div>
          <div style="width:14px;height:14px;background:rgba(63,176,168,0.45);border-radius:3px;"></div>
          <div style="width:14px;height:14px;background:rgba(63,176,168,0.7);border-radius:3px;"></div>
          <div style="width:14px;height:14px;background:#3FB0A8;border-radius:3px;"></div>
          <span>More</span>
        </div>
      </div>
    """, ["Timer", "Stats", "Settings"], "Stats")

    s3 = with_chrome(w, h, "Settings", base, """
      <div class="card" style="margin-bottom:16px;">
        <div style="font-size:22px;font-weight:500;margin-bottom:24px;">Intervals</div>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
          <span style="font-size:20px;opacity:0.85;">Focus session</span>
          <span style="font-size:24px;font-weight:600;color:#3FB0A8;">25 min</span>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
          <span style="font-size:20px;opacity:0.85;">Short break</span>
          <span style="font-size:24px;font-weight:600;color:#3FB0A8;">5 min</span>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
          <span style="font-size:20px;opacity:0.85;">Long break</span>
          <span style="font-size:24px;font-weight:600;color:#3FB0A8;">15 min</span>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span style="font-size:20px;opacity:0.85;">Sessions until long break</span>
          <span style="font-size:24px;font-weight:600;color:#3FB0A8;">4</span>
        </div>
      </div>
      <div class="card" style="margin-bottom:16px;">
        <div style="font-size:22px;font-weight:500;margin-bottom:20px;">Sound</div>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
          <span style="font-size:20px;opacity:0.85;">Background sound</span>
          <span style="font-size:20px;color:#3FB0A8;">Soft rain ▸</span>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
          <span style="font-size:20px;opacity:0.85;">Tick sound during focus</span>
          <div style="width:64px;height:36px;background:rgba(255,255,255,0.18);border-radius:18px;position:relative;">
            <div style="position:absolute;top:4px;left:4px;width:28px;height:28px;background:white;border-radius:50%;"></div>
          </div>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span style="font-size:20px;opacity:0.85;">Haptic on session end</span>
          <div style="width:64px;height:36px;background:#3FB0A8;border-radius:18px;position:relative;">
            <div style="position:absolute;top:4px;right:4px;width:28px;height:28px;background:white;border-radius:50%;"></div>
          </div>
        </div>
      </div>
      <div class="card">
        <div style="font-size:22px;font-weight:500;margin-bottom:20px;">Appearance</div>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
          <span style="font-size:20px;opacity:0.85;">Theme</span>
          <span style="font-size:20px;color:#3FB0A8;">Dark ▸</span>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span style="font-size:20px;opacity:0.85;">True black (OLED)</span>
          <div style="width:64px;height:36px;background:#3FB0A8;border-radius:18px;position:relative;">
            <div style="position:absolute;top:4px;right:4px;width:28px;height:28px;background:white;border-radius:50%;"></div>
          </div>
        </div>
      </div>
    """, ["Timer", "Stats", "Settings"], "Settings")
    return [s1, s2, s3]


def sound_meter_screens(w, h):
    base = ":root { --bg:#0E1116; --fg:#FFFFFF; --bar:#0E1116; --accent:#FFB020; --card:#1A2030; }"
    # Semicircular gauge SVG: 0–130 dB, with safe/moderate/loud/danger bands.
    def gauge(value_db):
        # Map 0–130 dB to 180–360 degrees (left half-circle)
        pct = max(0, min(130, value_db)) / 130.0
        # 180° sweep starting from 180°
        end_deg = 180 + pct * 180
        circumference = 3.14159 * 280  # half circle
        sweep = pct * circumference
        return f"""
        <svg viewBox="0 0 640 360" style="width:100%;height:100%;">
          <!-- background arc -->
          <path d="M 40,320 A 280,280 0 0 1 600,320" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="36" stroke-linecap="round"/>
          <!-- safe (green) -->
          <path d="M 40,320 A 280,280 0 0 1 168,72" fill="none" stroke="#34C759" stroke-width="36" stroke-linecap="round" opacity="0.85"/>
          <!-- moderate (yellow) -->
          <path d="M 168,72 A 280,280 0 0 1 472,72" fill="none" stroke="#FFCC00" stroke-width="36" stroke-linecap="round" opacity="0.85"/>
          <!-- danger (red) -->
          <path d="M 472,72 A 280,280 0 0 1 600,320" fill="none" stroke="#FF3B30" stroke-width="36" stroke-linecap="round" opacity="0.85"/>
          <!-- needle -->
          <g transform="rotate({end_deg - 180} 320 320)">
            <line x1="320" y1="320" x2="320" y2="60" stroke="#FFFFFF" stroke-width="6" stroke-linecap="round"/>
            <circle cx="320" cy="320" r="14" fill="#FFFFFF"/>
          </g>
        </svg>
        """

    s1 = with_chrome(w, h, "Sound Level Meter", base, f"""
      <div style="position:relative;width:100%;height:380px;margin-bottom:24px;">
        {gauge(72)}
      </div>
      <div style="text-align:center;margin-top:-40px;margin-bottom:32px;">
        <div style="font-size:120px;font-weight:300;letter-spacing:-2px;line-height:1;">72</div>
        <div style="font-size:24px;opacity:0.6;margin-top:8px;letter-spacing:4px;">dB SPL</div>
      </div>
      <div class="card" style="margin-bottom:14px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span style="font-size:22px;opacity:0.7;">Average</span>
          <span style="font-size:28px;font-weight:600;">68 dB</span>
        </div>
      </div>
      <div class="card" style="margin-bottom:14px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span style="font-size:22px;opacity:0.7;">Peak (last 30s)</span>
          <span style="font-size:28px;font-weight:600;color:#FFCC00;">82 dB</span>
        </div>
      </div>
      <div class="card" style="background:rgba(52,199,89,0.15);border:1.5px solid #34C759;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span style="font-size:22px;color:#34C759;">SAFE</span>
          <span style="font-size:18px;opacity:0.8;">Below WHO 85 dB limit</span>
        </div>
      </div>
    """, ["Meter", "History", "Settings"], "Meter")

    s2 = with_chrome(w, h, "History", base, """
      <div class="card" style="margin-bottom:16px;">
        <div style="font-size:18px;opacity:0.6;margin-bottom:8px;">Today's average</div>
        <div style="font-size:64px;font-weight:600;color:#FFCC00;">71 dB</div>
        <div style="font-size:18px;opacity:0.6;">Recorded over 2h 14m of measuring</div>
      </div>
      <div class="card" style="margin-bottom:14px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <div><div style="font-size:22px;">Coffee shop session</div><div style="font-size:16px;opacity:0.6;">Today, 09:42 · 45 min</div></div>
          <div style="text-align:right;"><div style="font-size:26px;font-weight:600;color:#FFCC00;">68 dB</div><div style="font-size:14px;opacity:0.6;">peak 81</div></div>
        </div>
      </div>
      <div class="card" style="margin-bottom:14px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <div><div style="font-size:22px;">Construction site</div><div style="font-size:16px;opacity:0.6;">Yesterday, 14:30 · 1h 12m</div></div>
          <div style="text-align:right;"><div style="font-size:26px;font-weight:600;color:#FF3B30;">94 dB</div><div style="font-size:14px;opacity:0.6;">peak 108</div></div>
        </div>
      </div>
      <div class="card" style="margin-bottom:14px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <div><div style="font-size:22px;">Home office</div><div style="font-size:16px;opacity:0.6;">Yesterday, 09:00 · 4h 02m</div></div>
          <div style="text-align:right;"><div style="font-size:26px;font-weight:600;color:#34C759;">42 dB</div><div style="font-size:14px;opacity:0.6;">peak 61</div></div>
        </div>
      </div>
      <div class="card" style="margin-bottom:14px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <div><div style="font-size:22px;">Restaurant</div><div style="font-size:16px;opacity:0.6;">Mon, 19:15 · 1h 38m</div></div>
          <div style="text-align:right;"><div style="font-size:26px;font-weight:600;color:#FFCC00;">76 dB</div><div style="font-size:14px;opacity:0.6;">peak 88</div></div>
        </div>
      </div>
    """, ["Meter", "History", "Settings"], "History")

    s3 = with_chrome(w, h, "Settings", base, """
      <div class="card" style="margin-bottom:16px;">
        <div style="font-size:22px;font-weight:500;margin-bottom:20px;">Calibration</div>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
          <span style="font-size:20px;opacity:0.85;">Offset</span>
          <span style="font-size:24px;font-weight:600;color:#FFB020;">+2 dB</span>
        </div>
        <div style="font-size:14px;opacity:0.55;line-height:1.4;">Adjust if your device reads consistently high or low compared with a known reference.</div>
      </div>
      <div class="card" style="margin-bottom:16px;">
        <div style="font-size:22px;font-weight:500;margin-bottom:20px;">Alert thresholds</div>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
          <span style="font-size:20px;opacity:0.85;">Moderate (WHO recommended)</span>
          <span style="font-size:22px;color:#FFCC00;">70 dB</span>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
          <span style="font-size:20px;opacity:0.85;">Loud — hearing risk</span>
          <span style="font-size:22px;color:#FF9500;">85 dB</span>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span style="font-size:20px;opacity:0.85;">Dangerous — protect ears</span>
          <span style="font-size:22px;color:#FF3B30;">100 dB</span>
        </div>
      </div>
      <div class="card">
        <div style="font-size:22px;font-weight:500;margin-bottom:20px;">Display</div>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
          <span style="font-size:20px;opacity:0.85;">Show peak hold</span>
          <div style="width:64px;height:36px;background:#FFB020;border-radius:18px;position:relative;">
            <div style="position:absolute;top:4px;right:4px;width:28px;height:28px;background:white;border-radius:50%;"></div>
          </div>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span style="font-size:20px;opacity:0.85;">Logarithmic scale</span>
          <div style="width:64px;height:36px;background:#FFB020;border-radius:18px;position:relative;">
            <div style="position:absolute;top:4px;right:4px;width:28px;height:28px;background:white;border-radius:50%;"></div>
          </div>
        </div>
      </div>
    """, ["Meter", "History", "Settings"], "Settings")
    return [s1, s2, s3]


APPS = [
    ("ws_001_tipcalcdeluxe",    tipcalc_screens),
    ("ws_002_unitconverterpro", unitconv_screens),
    ("ws_003_soundlevelmeter",  sound_meter_screens),
    ("ws_004_qrbarcodescanner", qr_screens),
    ("ws_005_pomodorofocus",    pomodoro_screens),
]


async def render(page, html, w, h, out_path):
    await page.set_viewport_size({"width": w, "height": h})
    await page.set_content(html)
    await page.wait_for_timeout(150)
    await page.screenshot(path=str(out_path), type="png",
                          clip={"x": 0, "y": 0, "width": w, "height": h})
    print(f"    {out_path.name}")


async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page    = await browser.new_page()
        for ws, builder in APPS:
            od = images_dir(ws)
            print(f"\n[{ws}]")
            for label, w, h in [("screen", 1080, 1920),
                                 ("tablet7", 1200, 1920),
                                 ("tablet10", 1600, 2560)]:
                screens = builder(w, h)
                for i, html in enumerate(screens, 1):
                    out = od / f"{label}_{i}.png"
                    await render(page, html, w, h, out)
        await browser.close()
    print("\n[DONE]")


if __name__ == "__main__":
    asyncio.run(main())
