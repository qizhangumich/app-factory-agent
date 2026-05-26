# Launch Checklist — Unit Converter Pro

> Generated 2026-05-27 by `scripts/generate_launch_docs.py`.
> Source of truth: `config/play_content_declarations.yaml`.

This is the **one-time Play Console UI clickthrough** for this app. Everything
else (AAB upload, listing text, images, privacy URL) is automated by
`scripts/play_release.py`. After completing this checklist, that one command
ships the app end-to-end.

---

## Identity

| Field | Value |
|-------|-------|
| App name | `Unit Converter Pro` |
| Package name | `com.appfactory.unitconverterpro` |
| Workspace | `ws_002_unitconverterpro` |
| Category | `Tools` |
| Tagline | 50+ unit types, instant results |
| Developer | LINKWAVE PTE.LTD. (account ID `6960516323590864406`) |

---

## URLs & contact

| Field | Value |
|-------|-------|
| Privacy policy URL | `https://qizhangumich.github.io/app-privacy/unitconverterpro.html` |
| Developer contact email | `developer_apple@linkwave.one` |
| Developer website | `https://qizhangumich.github.io/app-privacy/unitconverterpro.html` (or LinkWave site if available) |

---

## Step 1 — Create app in Play Console (~1 min)

URL: <https://play.google.com/console/u/0/developers/6960516323590864406/app-list>

1. Click **Create app**
2. Fill in:
   - **App name:** `Unit Converter Pro`
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
| URL | `https://qizhangumich.github.io/app-privacy/unitconverterpro.html` |

### 2. Ads
| Question | Answer |
|----------|--------|
| Does your app contain ads? | **No** |

### 3. App access
> All functionality is available without special access

### 4. Content rating (IARC questionnaire)
- **Category:** Utility, Productivity, Communication, or Other
- Answer **No** to every question:
  - Violence — No
  - Sexual content — No
  - Profanity — No
  - Crude humor — No
  - Controlled substances — No
  - Gambling — No
  - User-generated content — No
  - Location sharing — No
  - Personal info sharing — No
  - Digital purchases — No
- **Email:** `developer_apple@linkwave.one`
- **Expected rating:** Everyone / PEGI 3 / Rated 4+

### 5. Target audience and content
- **Target age groups:** 18 and over
- **Appeals to children:** No

### 6. Data safety
| Question | Answer |
|----------|--------|
| Does your app collect or share user data? | **No** |
| Is all data encrypted in transit? | **Yes** |
| Can users request data deletion? | **Yes** |
| Data types collected | (none) |
| Data types shared | (none) |

### 7. Advertising ID
| Question | Answer |
|----------|--------|
| Does your app use advertising ID? | **No** |

### 8. Government apps
| Question | Answer |
|----------|--------|
| Is this a government app? | **No** |

### 9. Financial features
| Question | Answer |
|----------|--------|
| Does your app provide financial features? | **No** |

### 10. Special categories (News, Health, COVID-19)
- News app — **No**
- Health app — **No**
- COVID-19 contact tracing app — **No**

---

## Step 3 — Run the pipeline

After every declaration shows green ✅ on the App content page, run:

```bash
python scripts/play_release.py --submit --only ws_002_unitconverterpro
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
`workspaces/ws_002_unitconverterpro/android/app/build.gradle.kts` and run:

```bash
python scripts/play_release.py --build --submit --only ws_002_unitconverterpro
```
