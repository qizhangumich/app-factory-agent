#!/usr/bin/env python3
"""
App Factory v2 — Per-App Launch Checklist Generator
=====================================================
Produces a single self-contained Markdown checklist per app that the
operator follows once in Play Console UI: the URLs, the developer email,
the privacy page, and the standard answers for all 10 App content
declarations.

Output: workspaces/<ws>/LAUNCH_CHECKLIST.md

Run:  python scripts/generate_launch_docs.py
"""

import sys
from pathlib import Path
from datetime import date

REPO_ROOT = Path(__file__).parent.parent.resolve()
CONFIG    = REPO_ROOT / "config" / "play_content_declarations.yaml"

DEVELOPER_EMAIL = "developer_apple@linkwave.one"
PRIVACY_BASE    = "https://qizhangumich.github.io/app-privacy"
PLAY_CONSOLE    = "https://play.google.com/console"
DEV_ID          = "6960516323590864406"

APPS = [
    {"ws": "ws_001_tipcalcdeluxe",    "name": "Tip Calculator Deluxe",
     "package": "com.appfactory.tipcalcdeluxe",    "slug": "tipcalcdeluxe",
     "category": "Tools",     "tagline": "Split any bill in seconds"},
    {"ws": "ws_002_unitconverterpro", "name": "Unit Converter Pro",
     "package": "com.appfactory.unitconverterpro", "slug": "unitconverterpro",
     "category": "Tools",     "tagline": "50+ unit types, instant results"},
    {"ws": "ws_004_qrbarcodescanner", "name": "QR & Barcode Scanner+",
     "package": "com.appfactory.qrbarcodescanner", "slug": "qrbarcodescanner",
     "category": "Tools",     "tagline": "Scan anything, instantly"},
    {"ws": "ws_005_pomodorofocus",    "name": "Pomodoro Focus Timer",
     "package": "com.appfactory.pomodorofocus",    "slug": "pomodorofocus",
     "category": "Productivity",  "tagline": "Deep work, one session at a time"},
]


def load_config():
    import yaml
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))


def merged(cfg, ws):
    overrides = (cfg.get("overrides") or {}).get(ws, {}) or {}
    out = {}
    for k, v in cfg.items():
        if k == "overrides":
            continue
        if isinstance(v, dict) and k in overrides:
            out[k] = {**v, **overrides[k]}
        else:
            out[k] = v
    return out


def yes_no(b):
    return "Yes" if b else "No"


def render(app, cfg) -> str:
    m = merged(cfg, app["ws"])
    privacy_url = f"{PRIVACY_BASE}/{app['slug']}.html"
    today = date.today().isoformat()

    return f"""# Launch Checklist — {app['name']}

> Generated {today} by `scripts/generate_launch_docs.py`.
> Source of truth: `config/play_content_declarations.yaml`.

This is the **one-time Play Console UI clickthrough** for this app. Everything
else (AAB upload, listing text, images, privacy URL) is automated by
`scripts/play_release.py`. After completing this checklist, that one command
ships the app end-to-end.

---

## Identity

| Field | Value |
|-------|-------|
| App name | `{app['name']}` |
| Package name | `{app['package']}` |
| Workspace | `{app['ws']}` |
| Category | `{app['category']}` |
| Tagline | {app['tagline']} |
| Developer | LINKWAVE PTE.LTD. (account ID `{DEV_ID}`) |

---

## URLs & contact

| Field | Value |
|-------|-------|
| Privacy policy URL | `{privacy_url}` |
| Developer contact email | `{DEVELOPER_EMAIL}` |
| Developer website | `{privacy_url}` (or LinkWave site if available) |

---

## Step 1 — Create app in Play Console (~1 min)

URL: <{PLAY_CONSOLE}/u/0/developers/{DEV_ID}/app-list>

1. Click **Create app**
2. Fill in:
   - **App name:** `{app['name']}`
   - **Default language:** English (United States)
   - **App or game:** App
   - **Free or paid:** Free
3. Check both declaration boxes (Developer Programme Policies, US export laws)
4. Click **Create app**

---

## Step 2 — Fill 10 "App content" declarations (~10 min)

Navigate to: **App → left sidebar → Policy and programmes → App content**

### 1. Privacy policy
| Field | Value |
|-------|-------|
| URL | `{privacy_url}` |

### 2. Ads
| Question | Answer |
|----------|--------|
| Does your app contain ads? | **{yes_no(m['ads']['contains_ads'])}** |

### 3. App access
> {m['app_access']['note']}

### 4. Content rating (IARC questionnaire)
- **Category:** {m['content_rating']['category']}
- Answer **{yes_no(False)}** to every question:
  - Violence — {yes_no(m['content_rating']['questions']['violence'])}
  - Sexual content — {yes_no(m['content_rating']['questions']['sexual_content'])}
  - Profanity — {yes_no(m['content_rating']['questions']['profanity'])}
  - Crude humor — {yes_no(m['content_rating']['questions']['crude_humor'])}
  - Controlled substances — {yes_no(m['content_rating']['questions']['controlled_substances'])}
  - Gambling — {yes_no(m['content_rating']['questions']['gambling'])}
  - User-generated content — {yes_no(m['content_rating']['questions']['user_generated_content'])}
  - Location sharing — {yes_no(m['content_rating']['questions']['location_sharing'])}
  - Personal info sharing — {yes_no(m['content_rating']['questions']['personal_info_sharing'])}
  - Digital purchases — {yes_no(m['content_rating']['questions']['digital_purchases'])}
- **Email:** `{DEVELOPER_EMAIL}`
- **Expected rating:** {m['content_rating']['expected_rating']}

### 5. Target audience and content
- **Target age groups:** {", ".join(m['target_audience']['age_groups'])}
- **Appeals to children:** {yes_no(m['target_audience']['appeals_to_children'])}

### 6. Data safety
| Question | Answer |
|----------|--------|
| Does your app collect or share user data? | **{yes_no(m['data_safety']['collects_data'])}** |
| Is all data encrypted in transit? | **{yes_no(m['data_safety']['encrypted_in_transit'])}** |
| Can users request data deletion? | **{yes_no(m['data_safety']['users_can_request_deletion'])}** |
| Data types collected | {", ".join(m['data_safety']['data_types_collected']) or "(none)"} |
| Data types shared | {", ".join(m['data_safety']['data_types_shared']) or "(none)"} |

### 7. Advertising ID
| Question | Answer |
|----------|--------|
| Does your app use advertising ID? | **{yes_no(m['advertising_id']['uses_advertising_id'])}** |

### 8. Government apps
| Question | Answer |
|----------|--------|
| Is this a government app? | **{yes_no(m['government_apps']['is_government_app'])}** |

### 9. Financial features
| Question | Answer |
|----------|--------|
| Does your app provide financial features? | **{yes_no(m['financial_features']['provides_financial_features'])}** |

### 10. Special categories (News, Health, COVID-19)
- News app — **{yes_no(m['special_categories']['is_news_app'])}**
- Health app — **{yes_no(m['special_categories']['is_health_app'])}**
- COVID-19 contact tracing app — **{yes_no(m['special_categories']['is_covid_app'])}**

---

## Step 3 — Run the pipeline

After every declaration shows green ✅ on the App content page, run:

```bash
python scripts/play_release.py --submit --only {app['ws']}
```

This uploads the signed AAB, the listing text, all images (icon,
feature graphic, phone + 7" + 10" tablet screenshots), sets the privacy
policy URL and contact email, then creates a production draft.

---

## Step 4 — Three final UI clicks (one-time per app — Google policy)

These cannot be automated for a brand-new app. After the pipeline finishes:

### 4a. Save the Main store listing once
- Play Console → app → **Grow → Main store listing**
- Everything is pre-filled by the API. Click in the Full description
  field, add a space and remove it, then click **Save** (this triggers
  Play Console to record the listing as "user-confirmed").

### 4b. Select countries/regions
- App → **Production → Countries/regions** tab
- Click **Add countries/regions** → tick "Select all" → **Add**.

### 4c. Send for review
- App → **Publishing overview** (under Dashboard)
- Click **"Send N changes for review"** (top right, blue button)
- Confirm

Google review takes 1–3 days for the first release. After approval the
app goes live automatically (`completed` rollout = 100% by default).

---

## Future releases (zero manual work)

For every subsequent release of this same app — bug fixes, new features,
new versions — manual work is zero. Just bump `versionCode` in
`workspaces/{app['ws']}/android/app/build.gradle.kts` and run:

```bash
python scripts/play_release.py --build --submit --only {app['ws']}
```
"""


def main():
    cfg = load_config()
    target = sys.argv[1] if len(sys.argv) > 1 else None

    for app in APPS:
        if target and app["ws"] != target:
            continue
        out_path = REPO_ROOT / "workspaces" / app["ws"] / "LAUNCH_CHECKLIST.md"
        out_path.write_text(render(app, cfg), encoding="utf-8")
        print(f"[ok]  {out_path.relative_to(REPO_ROOT)}")

    print("\nDone.")


if __name__ == "__main__":
    main()
