"""Render each workspace's master SVG icon into its iOS app-icon PNG.

The factory workers design a vector master icon at ``shared/app_icon.svg``.
The iOS asset catalog needs a 1024x1024 raster, and the App Store rejects
icons that carry an alpha channel — so this tool renders the SVG with
Chromium (via Playwright) onto an opaque background, then saves it as a
flat RGB PNG at the filename the asset catalog's Contents.json expects.

Android needs no raster: its launcher icons are adaptive vector XML.

Usage:
    python scripts/render_icons.py             # all workspaces
    python scripts/render_icons.py ws_001      # one workspace
"""
from __future__ import annotations

import glob
import io
import json
import os
import re
import sys

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIZE = 1024


def find_appicon_png(ws_dir: str) -> str | None:
    """Return the absolute path the 1024 app-icon PNG must be written to."""
    matches = glob.glob(os.path.join(
        ws_dir, "ios", "*", "Assets.xcassets", "AppIcon.appiconset", "Contents.json"))
    if not matches:
        return None
    contents_path = matches[0]
    with open(contents_path, "r", encoding="utf-8") as fh:
        contents = json.load(fh)
    filename = None
    for image in contents.get("images", []):
        if image.get("size") == "1024x1024" and image.get("filename"):
            filename = image["filename"]
            break
    if filename is None:
        filename = "AppIcon.png"
    return os.path.join(os.path.dirname(contents_path), filename)


def background_color(svg_text: str) -> str:
    """The icon's backdrop colour — the first gradient stop in the SVG."""
    match = re.search(r'stop-color="(#[0-9A-Fa-f]{3,8})"', svg_text)
    return match.group(1) if match else "#FFFFFF"


def svg_only(svg_text: str) -> str:
    """Drop the XML prolog / comments so the markup embeds cleanly in HTML."""
    idx = svg_text.find("<svg")
    return svg_text[idx:] if idx >= 0 else svg_text


def render(page, svg_text: str, bg: str) -> bytes:
    html = (
        "<!DOCTYPE html><html><head><meta charset='utf-8'><style>"
        f"html,body{{margin:0;padding:0;width:{SIZE}px;height:{SIZE}px;"
        f"background:{bg};}}svg{{display:block;width:{SIZE}px;height:{SIZE}px;}}"
        "</style></head><body>" + svg_only(svg_text) + "</body></html>"
    )
    page.set_content(html, wait_until="networkidle")
    return page.screenshot(clip={"x": 0, "y": 0, "width": SIZE, "height": SIZE})


def main() -> None:
    only = sys.argv[1] if len(sys.argv) > 1 else None
    ws_dirs = sorted(d for d in glob.glob(os.path.join(ROOT, "workspaces", "ws_*"))
                     if os.path.isdir(d) and (only is None or only in os.path.basename(d)))

    jobs = []
    for ws_dir in ws_dirs:
        svg_path = os.path.join(ws_dir, "shared", "app_icon.svg")
        png_path = find_appicon_png(ws_dir)
        if os.path.exists(svg_path) and png_path:
            jobs.append((os.path.basename(ws_dir), svg_path, png_path))

    if not jobs:
        print("no icon jobs found")
        return

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": SIZE, "height": SIZE})
        for ws_name, svg_path, png_path in jobs:
            with open(svg_path, "r", encoding="utf-8") as fh:
                svg_text = fh.read()
            png_bytes = render(page, svg_text, background_color(svg_text))
            image = Image.open(io.BytesIO(png_bytes)).convert("RGB")  # strip alpha
            image.save(png_path, format="PNG")
            rel = os.path.relpath(png_path, ROOT).replace("\\", "/")
            print(f"  {ws_name}: {image.size[0]}x{image.size[1]} RGB -> {rel}")
        browser.close()

    print(f"rendered {len(jobs)} app icon(s)")


if __name__ == "__main__":
    main()
