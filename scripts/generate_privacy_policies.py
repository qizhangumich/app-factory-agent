#!/usr/bin/env python3
"""
App Factory v2 — Privacy Policy Generator
==========================================
Generates compliant privacy policy HTML files for every Play app.
Each file names the publishing entity (LINKWAVE PTE.LTD.), the app, the
contact email, and the standard "no data collection" disclosure block —
the exact details Google requires for review approval.

Output: .privacy_site/<slug>.html (one per app) + index.html

Run:  python scripts/generate_privacy_policies.py
Then:
    cd .privacy_site && git add . && git commit -m "update policies" && git push
"""

from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
OUT_DIR   = REPO_ROOT / ".privacy_site"

# --- Publisher info (must match Play Console developer profile) -------------
DEVELOPER_LEGAL_NAME = "LINKWAVE PTE.LTD."
DEVELOPER_EMAIL      = "developer_apple@linkwave.one"
DEVELOPER_COUNTRY    = "Singapore"
PRIVACY_BASE_URL     = "https://qizhangumich.github.io/app-privacy"

APPS = [
    {"slug": "tipcalcdeluxe",
     "name": "Tip Calculator Deluxe",
     "color": "#0A84FF", "dark": "#005EC4",
     "stored": "Your last 20 tip calculations (amount, percentage, party size)",
     "permissions": "no special permissions",
     "internet": "The App works completely offline. It makes no network requests."},
    {"slug": "unitconverterpro",
     "name": "Unit Converter Pro",
     "color": "#4F46E5", "dark": "#3730A3",
     "stored": "Your favorite conversion pairs and the last 100 conversions",
     "permissions": "no special permissions",
     "internet": "The App works completely offline. It makes no network requests."},
    {"slug": "qrbarcodescanner",
     "name": "QR & Barcode Scanner+",
     "color": "#34C759", "dark": "#1E7A34",
     "stored": "Your scan history (decoded QR/barcode text and timestamps)",
     "permissions": "the camera permission, used solely to scan codes locally on your device",
     "internet": "The App works offline for scanning. Optional 'open URL' actions on a "
                 "decoded link launch your default browser, which is a separate app with "
                 "its own privacy policy. The App itself makes no network requests."},
    {"slug": "pomodorofocus",
     "name": "Pomodoro Focus Timer",
     "color": "#3FB0A8", "dark": "#2A7A74",
     "stored": "Your focus session history (start time, duration, completion status) "
               "and your custom interval settings",
     "permissions": "the notification permission, used to alert you when a focus or break "
                    "interval ends",
     "internet": "The App works completely offline. It makes no network requests."},
]


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Privacy Policy — {app_name}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
         max-width: 720px; margin: 0 auto; padding: 32px 20px 64px; color: #1c1c1e;
         line-height: 1.65; background: #ffffff; }}
  h1 {{ color: {color}; font-size: 1.9rem; margin-bottom: 4px; }}
  h2 {{ color: {dark}; font-size: 1.2rem; margin-top: 32px; }}
  .meta {{ color: #6e6e73; font-size: 0.92rem; margin-bottom: 24px; }}
  .meta strong {{ color: #1c1c1e; }}
  ul {{ padding-left: 22px; }}
  ul li {{ margin: 4px 0; }}
  a {{ color: {color}; }}
  footer {{ margin-top: 48px; font-size: 0.85rem; color: #888; border-top: 1px solid #eee; padding-top: 16px; }}
  .entity-box {{ background: #f5f5f7; border-radius: 12px; padding: 16px 20px; margin: 24px 0; }}
  .entity-box p {{ margin: 4px 0; }}
</style>
</head>
<body>

<h1>Privacy Policy for {app_name}</h1>

<div class="meta">
  <p><strong>App:</strong> {app_name} (Android, distributed via Google Play)</p>
  <p><strong>Publisher:</strong> {publisher}</p>
  <p><strong>Effective date:</strong> {effective_date}</p>
</div>

<div class="entity-box">
  <p><strong>Who we are.</strong> {app_name} is published by <strong>{publisher}</strong>,
  a company organised under the laws of {country}. References to "we," "us," or "our"
  in this Policy mean {publisher}.</p>
  <p>You can reach us at <a href="mailto:{email}">{email}</a> for any privacy-related
  question, request, or complaint.</p>
</div>

<p>This Privacy Policy explains how {publisher} (the publisher of {app_name})
handles your information when you use {app_name} (the "App"). The short version:
<strong>the App does not collect, transmit, or share any personal data about you.</strong>
The longer version below explains exactly how that works.</p>

<h2>1. Information We Collect From You</h2>
<p><strong>None.</strong> The App does not collect any personal information about you.
{publisher} operates no servers, no analytics back-end, no advertising network, and no
user accounts in connection with the App. We never see, receive, or store any data
that originated on your device.</p>

<h2>2. Information Stored Locally on Your Device</h2>
<p>To make the App useful between sessions, the App stores the following information
on your device using the operating system's standard local storage APIs:</p>
<ul>
  <li>{stored}.</li>
  <li>Your in-App preference and settings choices.</li>
</ul>
<p>This local data:</p>
<ul>
  <li>never leaves your device;</li>
  <li>is not transmitted to {publisher} or to any third party;</li>
  <li>can be cleared at any time from within the App's settings;</li>
  <li>is fully removed when you uninstall the App.</li>
</ul>

<h2>3. Network Access</h2>
<p>{internet}</p>

<h2>4. Device Permissions</h2>
<p>The App requests {permissions}. The App does not access your location, contacts,
photos, microphone, calendar, SMS, call logs, or accounts.</p>

<h2>5. Third-Party Services and SDKs</h2>
<p>The App does <strong>not</strong> include any of the following:</p>
<ul>
  <li>advertising networks or ad SDKs;</li>
  <li>analytics SDKs (Firebase, Google Analytics, Flurry, Mixpanel, etc.);</li>
  <li>crash-reporting SDKs (Crashlytics, Sentry, etc.);</li>
  <li>social-media SDKs or share-tracking SDKs;</li>
  <li>any other third-party data-collection technology.</li>
</ul>

<h2>6. Children's Privacy</h2>
<p>Because the App collects no personal information of any kind from anyone, it
complies with the Children's Online Privacy Protection Act (COPPA), the EU General
Data Protection Regulation (GDPR), and equivalent regulations worldwide regarding
the data privacy of users under 13.</p>

<h2>7. Your Rights (GDPR, CCPA, and similar laws)</h2>
<p>Because {publisher} holds no personal data about you in connection with the App,
there is nothing for us to access, correct, port, or erase. You can fully delete
all locally-stored data by uninstalling the App or by clearing the App's data from
your device's Settings.</p>

<h2>8. Security</h2>
<p>All App data remains on your device under the protection of your device's own
operating-system security model. {publisher} does not transmit, host, or process
any of your data.</p>

<h2>9. Changes to This Policy</h2>
<p>If this Privacy Policy changes, the updated version will be published at this
URL with an updated "Effective date" above. Because the App collects no data,
substantive changes are not expected.</p>

<h2>10. Contact</h2>
<p>If you have any question, complaint, or request regarding this Privacy Policy
or {app_name}, please contact {publisher} at
<a href="mailto:{email}">{email}</a>.</p>

<footer>
  &copy; {year} {publisher}. All rights reserved. {app_name} is an offline utility
  designed to respect your privacy by collecting nothing.
</footer>

</body>
</html>
"""


INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{publisher} — Privacy Policies</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
         max-width: 640px; margin: 64px auto; padding: 0 24px; color: #1c1c1e; line-height: 1.6; }}
  h1 {{ font-size: 1.8rem; }}
  ul {{ padding-left: 22px; }}
  a {{ color: #007aff; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .meta {{ color: #6e6e73; font-size: 0.9rem; margin-bottom: 24px; }}
</style>
</head>
<body>
<h1>{publisher} — Privacy Policies</h1>
<p class="meta">Privacy policies for the Android apps published by {publisher}. Contact:
<a href="mailto:{email}">{email}</a></p>
<ul>
{links}
</ul>
</body>
</html>
"""


def main():
    OUT_DIR.mkdir(exist_ok=True)
    today = date.today().isoformat()
    year  = date.today().year

    for app in APPS:
        out = OUT_DIR / f"{app['slug']}.html"
        out.write_text(HTML_TEMPLATE.format(
            app_name=app["name"],
            publisher=DEVELOPER_LEGAL_NAME,
            email=DEVELOPER_EMAIL,
            country=DEVELOPER_COUNTRY,
            effective_date=today,
            year=year,
            color=app["color"],
            dark=app["dark"],
            stored=app["stored"],
            permissions=app["permissions"],
            internet=app["internet"],
        ), encoding="utf-8")
        print(f"[ok] {out.relative_to(REPO_ROOT)}")

    links = "\n".join(
        f'  <li><a href="{app["slug"]}.html">{app["name"]}</a></li>' for app in APPS
    )
    (OUT_DIR / "index.html").write_text(INDEX_TEMPLATE.format(
        publisher=DEVELOPER_LEGAL_NAME, email=DEVELOPER_EMAIL, links=links
    ), encoding="utf-8")
    print(f"[ok] {(OUT_DIR / 'index.html').relative_to(REPO_ROOT)}")

    print("\nNext:")
    print("  cd .privacy_site && git add . && \\")
    print('    git commit -m "name LINKWAVE PTE.LTD. + contact email in every policy" && \\')
    print("    git push")
    print("  (Wait ~60s for GitHub Pages to redeploy, then re-submit the rejected apps.)")


if __name__ == "__main__":
    main()
