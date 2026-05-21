# APP FACTORY v2: Autonomous App Business Operating System

## Complete Instruction Book for Claude Code

**Version:** 2.1
**Date:** 2026-05-22
**Budget:** $800 seed capital
**Purpose:** Single source of truth. Claude Code executes everything without further human permission. Human touchpoints marked `[HUMAN GATE]`.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Budget Allocation: $800 Strategy](#2-budget-allocation-800-strategy)
3. [Architecture: Four Layers](#3-architecture-four-layers)
4. [Folder & File Structure](#4-folder--file-structure)
5. [Workspace Isolation: One App = One Universe](#5-workspace-isolation)
6. [Layer 1: Brain Agent](#6-layer-1-brain-agent)
7. [Layer 2: App Factory](#7-layer-2-app-factory)
8. [Layer 3: Delivery System (Fastlane CI/CD)](#8-layer-3-delivery-system)
9. [Layer 4: Human Gate (5%)](#9-layer-4-human-gate-5)
10. [Market Intelligence](#10-market-intelligence)
11. [App Scoring Matrix](#11-app-scoring-matrix)
12. [Target Categories & 20 Utility App Ideas](#12-target-categories--20-utility-app-ideas)
13. [Custom High-Value App Ideas](#13-custom-high-value-app-ideas)
14. [Pricing Strategy by Country](#14-pricing-strategy-by-country)
15. [ASO & Localization Strategy](#15-aso--localization-strategy)
16. [Account Management & Unlock Rules](#16-account-management--unlock-rules)
17. [The Sleepless Loop](#17-the-sleepless-loop)
18. [Parallel Execution Model](#18-parallel-execution-model)
19. [Risk Management](#19-risk-management)
20. [Pipeline Launch Manifest (First 24 Apps)](#20-pipeline-launch-manifest)
21. [Week-by-Week Execution Plan](#21-week-by-week-execution-plan)
22. [File Specifications](#22-file-specifications)
23. [Claude Code Execution Rules](#23-claude-code-execution-rules)

---

## 1. System Overview

This system is an autonomous, self-sustaining app business that:

- Starts with **$800** allocated across iOS + Android accounts from day 1
- Uses **AI (Claude Code) to make 100% of development decisions**
- Ships **paid apps** with **zero server costs** (with two exceptions — see Custom Apps)
- Has a **Fastlane-powered delivery system** that automates build, sign, screenshot, and upload
- Runs **24/7 as a sleepless agent** with state persistence on disk
- Targets **175 iOS countries + 176 Android countries** simultaneously
- Requires human only for **initial Fastlane setup and final submission approval (~5%)**

### Core Philosophy

- **Deny human subjective intentions** — AI decides what apps to build
- **No subscriptions, no ads, no servers** — paid download only (exceptions noted)
- **Volume over perfection** — ship fast, test market, compound winners
- **$800 is ALL the capital** — system must become self-sustaining
- **Every account must prove itself** — 3x return before funding expansion
- **Delivery is automated** — Fastlane handles build/sign/upload/metadata

---

## 2. Budget Allocation: $800 Strategy

### Day 1 Allocation

```
TOTAL BUDGET: $800

iOS Accounts (6 × $99/year = $594):
├── ios_001: Primary — Utilities & Productivity apps
├── ios_002: Health & Fitness apps
├── ios_003: Education & Reference apps
├── ios_004: Photography & Creative tools
├── ios_005: Custom apps (Global Bidding, Token Wallet)
├── ios_006: Reserve / Overflow account
│
Android Accounts (6 × $25 one-time = $150):
├── android_001: Mirror top iOS utilities
├── android_002: Mirror top iOS health/education
├── android_003: Mirror top iOS photo/creative
├── android_004: Custom apps (Global Bidding, Token Wallet)
├── android_005: Reserve / Overflow
├── android_006: Reserve / Overflow
│
Remaining: $800 - $594 - $150 = $56 emergency reserve
└── Held for: App Review expedite, domain registration, or 7th Android account
```

### Why 6 iOS + 6 Android From Day 1

1. **Risk distribution** — if Apple flags one account, you have 5 others running
2. **Category separation** — Apple less likely to flag "spam" if each account has a coherent category focus
3. **Parallel shipping** — 6 accounts × 5 apps/week = 30 apps/week capacity
4. **Android is dirt cheap** — $25 one-time, permanent, unlimited apps
5. **Dual-publish from day 1** — every iOS app gets an Android version immediately

### Revenue Rules (Updated for $800)

| Threshold | Action |
|-----------|--------|
| Any account earned $99 | Breakeven for that iOS slot confirmed |
| Any account earned $297 | 3x proven — can fund expansion if needed |
| Total revenue > $800 | Full system breakeven. Pure profit from here |
| Reserve fund < $50 | Pause new account creation until replenished |
| Account earns $0 for 60 days | Freeze submissions, redistribute apps to other accounts |

---

## 3. Architecture: Four Layers

```
┌─────────────────────────────────────────────────────────────┐
│                   LAYER 1: BRAIN AGENT                       │
│               (Strategic Decision Engine)                     │
│                                                              │
│  Market Scanner → App Scorer → Pricing Optimizer              │
│  Revenue Tracker → Account Manager → Kill/Boost Engine        │
│  Localization Planner → Platform Router (iOS vs Android)      │
│                         │                                    │
│              ┌──────────▼──────────┐                         │
│              │   BUILD QUEUE       │                         │
│              │  (state/queue.json) │                         │
│              └──────────┬──────────┘                         │
└─────────────────────────┼────────────────────────────────────┘
                          │ spec.json
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  LAYER 2: APP FACTORY                         │
│             (Claude Code Worker Sessions)                     │
│                                                              │
│  Code Gen (SwiftUI/Kotlin) → ASO Gen → Icon Gen               │
│  Screenshot Gen → Privacy Policy Gen → Localization Gen       │
│                         │                                    │
│              ┌──────────▼──────────┐                         │
│              │ Complete project     │                         │
│              │ (Xcode/Gradle)      │                         │
│              └──────────┬──────────┘                         │
└─────────────────────────┼────────────────────────────────────┘
                          │ project files
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              LAYER 3: DELIVERY SYSTEM                         │
│          (Fastlane + GitHub Actions CI/CD)                    │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────────┐   │
│  │ fastlane   │  │ fastlane   │  │ fastlane             │   │
│  │ match      │  │ gym/gradle │  │ deliver/supply       │   │
│  │ (signing)  │  │ (build)    │  │ (upload to stores)   │   │
│  └────────────┘  └────────────┘  └──────────────────────┘   │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────────┐   │
│  │ fastlane   │  │ fastlane   │  │ fastlane             │   │
│  │ snapshot   │  │ frameit    │  │ pilot/submit         │   │
│  │ (screens)  │  │ (frames)   │  │ (TestFlight/Review)  │   │
│  └────────────┘  └────────────┘  └──────────────────────┘   │
└─────────────────────────┼────────────────────────────────────┘
                          │ Uploaded binary + metadata
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              LAYER 4: HUMAN GATE (5%)                         │
│                                                              │
│   1. [ONCE] Set up Fastlane certificates + API keys          │
│   2. [PER APP] Review Fastlane output, approve submission    │
│   3. [IF REJECTED] Read rejection, trigger factory fix       │
└─────────────────────────┬────────────────────────────────────┘
                          │ Revenue flows back
                          ▼
                   ┌──────────────┐
                   │ App Store /  │──── Revenue feedback ──→ Brain
                   │ Google Play  │
                   └──────────────┘
```

---

## 4. Folder & File Structure

```
app-factory/
│
├── brain/                          # Layer 1: Brain Agent
│   ├── brain.py                    # Main orchestrator loop
│   ├── market_scanner.py           # Analyzes ranks.csv for opportunities
│   ├── app_scorer.py               # Scores ideas on 6 dimensions
│   ├── pricing_optimizer.py        # Sets price tiers per country
│   ├── localization_planner.py     # Picks languages per app
│   ├── account_manager.py          # Tracks 12 accounts (6 iOS + 6 Android)
│   ├── platform_router.py          # Decides iOS-first, Android-first, or dual
│   ├── revenue_tracker.py          # Monitors earnings, triggers decisions
│   └── kill_boost.py               # Marks dead apps, flags winners
│
├── factory/                        # Layer 2: App Factory
│   ├── factory.py                  # Worker reads spec → produces project
│   ├── ios_generator.py            # Generates SwiftUI Xcode project
│   ├── android_generator.py        # Generates Kotlin/Compose Android project
│   ├── aso_generator.py            # Writes App Store / Play Store metadata
│   ├── icon_generator.py           # Produces app icon assets (all sizes)
│   ├── screenshot_generator.py     # Generates device-frame screenshots
│   ├── privacy_policy_generator.py # Creates required privacy policy
│   ├── templates/
│   │   ├── ios/                    # SwiftUI templates
│   │   │   ├── base_app/
│   │   │   ├── utility_template/
│   │   │   ├── health_template/
│   │   │   ├── education_template/
│   │   │   ├── photo_template/
│   │   │   ├── timer_template/
│   │   │   ├── sound_template/
│   │   │   └── custom_template/    # For bidding/token wallet apps
│   │   └── android/                # Kotlin/Compose templates
│   │       ├── base_app/
│   │       ├── utility_template/
│   │       └── custom_template/
│   └── custom_apps/                # High-value custom app specs
│       ├── global_bidding_hub.json
│       ├── token_wallet.json
│       └── llm_token_marketplace.json
│
├── delivery/                       # Layer 3: Delivery System
│   ├── Gemfile                     # Ruby dependencies (fastlane)
│   ├── Fastfile                    # Master Fastfile with all lanes
│   ├── Matchfile                   # Code signing config
│   ├── Deliverfile                 # App Store upload config
│   ├── Supplyfile                  # Google Play upload config
│   ├── metadata/                   # Fastlane metadata structure
│   │   └── {app_bundle_id}/
│   │       ├── en-US/
│   │       │   ├── title.txt
│   │       │   ├── subtitle.txt
│   │       │   ├── description.txt
│   │       │   ├── keywords.txt
│   │       │   └── release_notes.txt
│   │       ├── ja/
│   │       ├── de-DE/
│   │       └── screenshots/
│   ├── scripts/
│   │   ├── deploy_ios.sh           # One-command iOS deploy
│   │   ├── deploy_android.sh       # One-command Android deploy
│   │   └── deploy_all.sh           # Deploy to both platforms
│   └── github_actions/
│       ├── ios_deploy.yml          # GitHub Actions workflow for iOS
│       └── android_deploy.yml      # GitHub Actions workflow for Android
│
├── data/                           # Market intelligence
│   ├── ranks.csv                   # Global app rankings (800K+ rows)
│   ├── market_analysis.json
│   ├── genre_competition.json
│   └── country_spending.json
│
├── state/                          # Persistent state (survives restarts)
│   ├── state.json                  # Brain state & phase
│   ├── queue.json                  # Build queue
│   ├── accounts.json               # All 12 developer accounts
│   ├── apps.json                   # All apps: status, revenue, metadata
│   ├── revenue.json                # Revenue per app/account/day
│   ├── build_log.json              # Build history
│   └── decisions.json              # Brain decision log with reasoning
│
├── queue/                          # Work queue (brain → factory → delivery)
│   ├── pending/                    # Specs waiting to be built
│   ├── building/                   # Currently being built
│   ├── built/                      # Built, awaiting delivery
│   ├── delivering/                 # Being uploaded by Fastlane
│   ├── submitted/                  # Submitted to store review
│   ├── live/                       # Approved and live
│   └── failed/                     # Failed (build or review)
│
├── workspaces/                     # ISOLATED per-app workspaces (see Section 5)
│   ├── ws_001_unitconverterpro/    # Each app is a self-contained universe
│   │   ├── workspace.json          # Manifest: accounts, platforms, status
│   │   ├── status.json             # Pipeline progress per platform
│   │   ├── spec.json               # Brain's original spec (read-only copy)
│   │   ├── result.json             # Factory's build output
│   │   ├── ios/                    # Complete Xcode project + fastlane/
│   │   ├── android/                # Complete Gradle project + fastlane/
│   │   └── shared/                 # Icons, privacy policy, shared assets
│   ├── ws_002_qrbarcodescanner/
│   └── ...
│   └── archive/                    # Killed apps moved here after 90 days
│
├── output/                         # DEPRECATED — use workspaces/ instead
│
├── config/
│   ├── config.yaml                 # Global settings
│   ├── apple_price_tiers.json
│   ├── genre_map.json
│   ├── accounts_config.yaml        # Account allocation strategy
│   └── fastlane_env/               # Per-account Fastlane credentials
│       ├── ios_001.env
│       ├── ios_002.env
│       ├── android_001.env
│       └── ...
│
├── scripts/
│   ├── setup.sh                    # One-time full environment setup
│   ├── setup_fastlane.sh           # Fastlane + certificates setup
│   ├── run_brain.sh                # Start brain loop
│   ├── run_factory.sh              # Start factory worker
│   ├── run_delivery.sh             # Start delivery pipeline
│   └── update_revenue.sh           # Pull revenue from stores
│
└── docs/
    └── APP_FACTORY_INSTRUCTION_BOOK.md
```

---

## 5. Workspace Isolation: One App = One Universe

### The Problem

Without isolation, projects bleed into each other:
- Shared Xcode derived data cache corrupts builds
- Asset catalog names collide (two apps both have `icon.png`)
- `Info.plist` from app A leaks into app B's build
- Fastlane credentials for account ios_001 accidentally sign app meant for ios_003
- A failed build leaves artifacts that poison the next app's build
- Two factory workers building simultaneously overwrite each other's temp files

### The Rule: Every App is a Self-Contained Universe

Each app project must be a **completely independent, portable directory** that contains everything needed to build, sign, and submit that app — with zero dependencies on any other app or shared state.

### Workspace Architecture

```
workspaces/                              # ALL app work happens here
│
├── ws_001_unitconverterpro/             # Workspace ID = sequential + slug
│   │
│   ├── workspace.json                   # Workspace manifest (links to brain state)
│   │
│   ├── ios/                             # iOS project (complete, self-contained)
│   │   ├── UnitConverterPro.xcodeproj/
│   │   ├── UnitConverterPro/
│   │   │   ├── App.swift
│   │   │   ├── ContentView.swift
│   │   │   ├── Models/
│   │   │   ├── Views/
│   │   │   ├── Resources/
│   │   │   │   ├── Assets.xcassets/     # App-specific icons + colors
│   │   │   │   └── Localizable.strings  # App-specific strings
│   │   │   └── Info.plist               # App-specific config
│   │   ├── UnitConverterProTests/
│   │   ├── build/                       # Build artifacts (gitignored)
│   │   └── fastlane/                    # Per-app Fastlane config
│   │       ├── Fastfile                 # App-specific lanes
│   │       ├── Appfile                  # Bundle ID + account for THIS app
│   │       ├── Deliverfile              # THIS app's upload config
│   │       └── metadata/
│   │           ├── en-US/
│   │           │   ├── title.txt
│   │           │   ├── subtitle.txt
│   │           │   ├── description.txt
│   │           │   ├── keywords.txt
│   │           │   └── release_notes.txt
│   │           ├── ja/
│   │           ├── de-DE/
│   │           └── screenshots/
│   │               ├── en-US/
│   │               ├── ja/
│   │               └── de-DE/
│   │
│   ├── android/                         # Android project (complete, self-contained)
│   │   ├── app/
│   │   │   ├── src/main/
│   │   │   │   ├── java/com/appfactory/unitconverterpro/
│   │   │   │   ├── res/
│   │   │   │   └── AndroidManifest.xml
│   │   │   └── build.gradle.kts
│   │   ├── build.gradle.kts
│   │   ├── settings.gradle.kts
│   │   ├── gradle.properties
│   │   ├── build/                       # Build artifacts (gitignored)
│   │   └── fastlane/
│   │       ├── Fastfile
│   │       ├── Appfile
│   │       ├── Supplyfile
│   │       └── metadata/
│   │           └── android/
│   │               ├── en-US/
│   │               └── ja/
│   │
│   ├── shared/                          # Shared between platforms (for this app only)
│   │   ├── privacy_policy.html
│   │   ├── app_icon_1024.png            # Master icon (platform-specific sizes generated)
│   │   └── assets/                      # Any shared data files
│   │
│   ├── spec.json                        # The brain's original build spec (read-only copy)
│   ├── result.json                      # Factory's build result
│   └── status.json                      # Current status in the pipeline
│
├── ws_002_qrbarcodescanner/
│   ├── workspace.json
│   ├── ios/
│   ├── android/
│   ├── shared/
│   ├── spec.json
│   ├── result.json
│   └── status.json
│
└── ... (one workspace per app, forever)
```

### workspace.json (Per-App Manifest)

```json
{
  "workspace_id": "ws_001",
  "app_slug": "unitconverterpro",
  "app_name": "Unit Converter Pro",
  "bundle_id_ios": "com.appfactory.unitconverterpro",
  "bundle_id_android": "com.appfactory.unitconverterpro",
  "ios_account": "ios_001",
  "android_account": "android_001",
  "platforms": ["ios", "android"],
  "created_at": "2026-05-22T10:00:00Z",
  "status": "building",
  "pipeline_stage": "factory",
  "build_history": [
    {"stage": "spec_created", "at": "2026-05-22T10:00:00Z"},
    {"stage": "factory_started", "at": "2026-05-22T10:05:00Z"}
  ]
}
```

### status.json (Pipeline Tracker Per App)

```json
{
  "workspace_id": "ws_001",
  "ios": {
    "code": "complete",
    "build": "pending",
    "sign": "pending",
    "upload": "pending",
    "review": "pending",
    "live": false
  },
  "android": {
    "code": "complete",
    "build": "pending",
    "sign": "pending",
    "upload": "pending",
    "review": "pending",
    "live": false
  }
}
```

### Isolation Rules

| Rule | Why |
|------|-----|
| **No shared build directories** | Xcode derived data for app A must never touch app B |
| **No shared Fastlane configs** | Each app has its own Appfile pointing to its own account + bundle ID |
| **No shared assets** | Each `Assets.xcassets` is fully self-contained. No symlinks |
| **No shared Info.plist** | Bundle ID, version, display name are all per-app |
| **Templates are copied, not linked** | Factory copies template into workspace; workspace never reads from templates/ after creation |
| **Build artifacts are per-workspace** | `build/` folder inside each workspace. Never a global build cache |
| **One factory worker = one workspace at a time** | Worker enters workspace, does all work there, exits. No parallel writes to same workspace |
| **Workspace is the unit of movement** | When moving from `building` → `built` → `delivering` → `live`, the ENTIRE workspace moves |

### Factory Worker Lifecycle (Isolated)

```python
def build_app(self, spec):
    # 1. Create isolated workspace
    ws_id = f"ws_{self.next_id():04d}_{spec['slug']}"
    ws_path = f"workspaces/{ws_id}"
    os.makedirs(ws_path, exist_ok=True)

    # 2. Copy spec into workspace (read-only reference)
    shutil.copy(spec_path, f"{ws_path}/spec.json")

    # 3. Copy template into workspace (template becomes owned by workspace)
    if "ios" in spec["platforms"]:
        template = f"factory/templates/ios/{spec['template']}"
        shutil.copytree(template, f"{ws_path}/ios", dirs_exist_ok=True)

    if "android" in spec["platforms"]:
        template = f"factory/templates/android/{spec['template']}"
        shutil.copytree(template, f"{ws_path}/android", dirs_exist_ok=True)

    # 4. Generate code INSIDE the workspace (never outside)
    os.chdir(ws_path)  # All work happens inside the workspace
    self.generate_ios_code(spec, f"{ws_path}/ios")
    self.generate_android_code(spec, f"{ws_path}/android")
    self.generate_shared_assets(spec, f"{ws_path}/shared")
    self.generate_fastlane_configs(spec, ws_path)

    # 5. Write workspace manifest
    self.write_workspace_json(spec, ws_path)

    # 6. Write status
    self.write_status_json(ws_path, stage="built")

    # 7. Return to root (leave workspace clean)
    os.chdir(self.root_dir)

    return ws_path
```

### Per-App Fastlane Appfile (Inside Each Workspace)

```ruby
# workspaces/ws_001_unitconverterpro/ios/fastlane/Appfile

app_identifier "com.appfactory.unitconverterpro"  # THIS app only
apple_id ENV["APPLE_ID_IOS_001"]                   # THIS account only
team_id ENV["TEAM_ID_IOS_001"]                     # THIS team only
```

```ruby
# workspaces/ws_001_unitconverterpro/android/fastlane/Appfile

package_name "com.appfactory.unitconverterpro"
json_key_file ENV["PLAY_JSON_KEY_ANDROID_001"]
```

### How Delivery Knows Which Account to Use

The delivery system reads `workspace.json` to determine credentials:

```bash
#!/bin/bash
# delivery/scripts/deploy_workspace.sh
# Usage: ./deploy_workspace.sh workspaces/ws_001_unitconverterpro

WS_PATH=$1
WS_JSON="${WS_PATH}/workspace.json"

# Extract account IDs from workspace manifest
IOS_ACCOUNT=$(python3 -c "import json; print(json.load(open('${WS_JSON}'))['ios_account'])")
ANDROID_ACCOUNT=$(python3 -c "import json; print(json.load(open('${WS_JSON}'))['android_account'])")

# Load account-specific credentials
source config/fastlane_env/${IOS_ACCOUNT}.env

# Deploy iOS (from within the workspace)
cd "${WS_PATH}/ios"
bundle exec fastlane ios deploy

# Deploy Android
source config/fastlane_env/${ANDROID_ACCOUNT}.env
cd "${WS_PATH}/android"
bundle exec fastlane android deploy

# Update workspace status
python3 brain/update_workspace_status.py "${WS_PATH}" "delivering"
```

### Pipeline Movement (Workspace as Unit)

```
Brain creates spec
    → spec.json written to queue/pending/

Factory picks up spec
    → Creates workspaces/ws_001_unitconverterpro/
    → Copies template INTO workspace
    → Generates ALL code inside workspace
    → Writes result.json + status.json
    → Updates queue: pending → built

Delivery picks up workspace
    → Reads workspace.json for account credentials
    → cd into workspace/ios/ → fastlane build + upload
    → cd into workspace/android/ → fastlane build + upload
    → Updates status.json: upload complete
    → Updates queue: built → submitted

Apple/Google approves
    → Updates status.json: live = true
    → Brain reads status, updates revenue tracking

EVERYTHING stays inside the workspace. Nothing leaks out.
```

### Cleanup Policy

| Rule | When |
|------|------|
| Keep workspace forever if app is live | Revenue tracking needs the reference |
| Archive workspace if app is killed | Move to `workspaces/archive/` after 90 days |
| Delete build artifacts | `*/build/` directories can be purged after submission |
| Never delete spec.json or result.json | Brain needs the audit trail |

---

## 6. Layer 1: Brain Agent

### Purpose
Strategic decision engine. Never writes app code. Only makes decisions:
- What to build (scoring)
- Where to sell (country targeting)
- At what price (tier optimization)
- On which platform (iOS vs Android vs both)
- Which account to use (load balancing across 12 accounts)
- When to kill or boost an app
- When to trigger localization expansion

### brain.py Core Logic

The brain runs every 30 minutes. Each cycle:

1. **Load state** from disk (state.json, accounts.json, revenue.json)
2. **Check revenue** — update per-app and per-account earnings
3. **Run kill/boost** — apps earning $0 after 30 days get killed; apps earning $10+ in week 1 get flagged for localization expansion
4. **Check account health** — flag frozen accounts, balance app distribution
5. **Platform routing** — decide iOS-first, Android-first, or dual based on genre
6. **Refill queue** — if pending < 5, scan market, score ideas, generate specs
7. **Save state** to disk
8. **Log decisions** with reasoning to decisions.json

### Platform Router Logic

```python
def route_platform(self, idea):
    """Decide which platform(s) to target."""
    category = idea["category"]

    # Utilities, Productivity, Health → iOS first (higher ARPU)
    if category in ["Utilities", "Productivity", "Health & Fitness"]:
        return {"primary": "ios", "secondary": "android", "delay_secondary": 7}

    # Games, Entertainment → dual publish (volume matters)
    if category in ["Games", "Entertainment"]:
        return {"primary": "both", "secondary": None, "delay_secondary": 0}

    # Education → dual (students on both platforms)
    if category in ["Education", "Reference"]:
        return {"primary": "both", "secondary": None, "delay_secondary": 0}

    # Custom apps → dual always
    if category in ["Custom"]:
        return {"primary": "both", "secondary": None, "delay_secondary": 0}

    # Default: iOS first
    return {"primary": "ios", "secondary": "android", "delay_secondary": 14}
```

### Account Load Balancer

```python
def assign_account(self, spec):
    """Assign app to the right account based on category allocation."""
    category = spec["category"]
    platform = spec["platform"]

    if platform == "ios":
        mapping = {
            "Utilities": "ios_001", "Productivity": "ios_001",
            "Health & Fitness": "ios_002",
            "Education": "ios_003", "Reference": "ios_003",
            "Photography": "ios_004",
            "Custom": "ios_005",
        }
        account_id = mapping.get(category, "ios_006")  # overflow to ios_006
    else:
        mapping = {
            "Utilities": "android_001", "Productivity": "android_001",
            "Health & Fitness": "android_002", "Education": "android_002",
            "Photography": "android_003",
            "Custom": "android_004",
        }
        account_id = mapping.get(category, "android_005")

    # Check if account is frozen → redirect to overflow
    account = self.accounts.get(account_id)
    if account["status"] == "frozen":
        account_id = "ios_006" if platform == "ios" else "android_006"

    return account_id
```

---

## 7. Layer 2: App Factory

Same as v1 but now generates BOTH iOS (SwiftUI) and Android (Kotlin/Jetpack Compose) projects from a single spec. The factory reads `spec.platform` to determine output:

- `platform: "ios"` → SwiftUI Xcode project
- `platform: "android"` → Kotlin/Compose Gradle project
- `platform: "both"` → generates both in parallel

### Code Rules (iOS - SwiftUI)
- Pure SwiftUI, iOS 16+, iPhone + iPad
- CoreData for persistence, UserDefaults for settings
- NO networking, NO API calls (exceptions: Custom Apps only)
- Dark mode + accessibility labels required
- No third-party dependencies (no CocoaPods, no SPM packages)

### Code Rules (Android - Kotlin/Compose)
- Jetpack Compose, minSdk 26 (Android 8.0+)
- Room for persistence, SharedPreferences for settings
- Material 3 design system
- NO networking (exceptions: Custom Apps only)
- No third-party dependencies beyond AndroidX

---

## 8. Layer 3: Delivery System (Fastlane CI/CD)

### Purpose
Automate EVERYTHING between "code is written" and "app is in the store." The factory drops a finished project; the delivery system builds it, signs it, generates screenshots, uploads metadata, and submits for review — all with one command.

### Fastlane Setup (One-Time, [HUMAN GATE])

```bash
# Install Fastlane
gem install fastlane

# Initialize for iOS
cd output/ios/{app_slug}
fastlane init

# Set up code signing with match (stores certs in private git repo)
fastlane match init
fastlane match appstore  # Creates/downloads App Store signing certs

# Set up App Store Connect API key (avoids 2FA issues on CI)
# Generate key at: https://appstoreconnect.apple.com/access/api
# Save as: config/fastlane_env/AuthKey_{KEY_ID}.p8
```

### Fastfile (Master)

```ruby
# delivery/Fastfile

platform :ios do
  desc "Build, sign, and upload iOS app to App Store Connect"
  lane :deploy do |options|
    app_dir = options[:app_dir]

    # Sync signing certificates
    match(type: "appstore", app_identifier: options[:bundle_id])

    # Build the app
    gym(
      scheme: options[:scheme],
      project: "#{app_dir}/#{options[:scheme]}.xcodeproj",
      output_directory: "#{app_dir}/build",
      clean: true,
      export_method: "app-store"
    )

    # Upload metadata + binary to App Store Connect
    deliver(
      app_identifier: options[:bundle_id],
      ipa: "#{app_dir}/build/#{options[:scheme]}.ipa",
      metadata_path: "#{app_dir}/metadata",
      screenshots_path: "#{app_dir}/metadata/screenshots",
      submit_for_review: false,  # Human approves final submit
      automatic_release: false,
      force: true,               # Skip HTML preview
      precheck_include_in_app_purchases: false
    )
  end

  desc "Generate screenshots using snapshot"
  lane :screenshots do |options|
    snapshot(
      project: options[:project],
      scheme: options[:scheme],
      output_directory: "#{options[:app_dir]}/metadata/screenshots",
      languages: ["en-US", "ja", "de-DE", "ko", "zh-Hans"],
      devices: [
        "iPhone 15 Pro Max",
        "iPhone 15 Pro",
        "iPad Pro (12.9-inch) (6th generation)"
      ]
    )
    frameit(path: "#{options[:app_dir]}/metadata/screenshots")
  end
end

platform :android do
  desc "Build and upload Android app to Google Play"
  lane :deploy do |options|
    gradle(
      project_dir: options[:app_dir],
      task: "bundleRelease"
    )

    supply(
      package_name: options[:bundle_id],
      aab: "#{options[:app_dir]}/app/build/outputs/bundle/release/app-release.aab",
      track: "production",
      metadata_path: "#{options[:app_dir]}/metadata",
      skip_upload_metadata: false,
      skip_upload_images: false,
      skip_upload_screenshots: false
    )
  end
end
```

### deploy_ios.sh (One-Command Deploy)

```bash
#!/bin/bash
# Usage: ./deploy_ios.sh <app_slug> <bundle_id> <scheme> <account_env>
APP_SLUG=$1
BUNDLE_ID=$2
SCHEME=$3
ACCOUNT_ENV=$4

# Load account-specific credentials
source config/fastlane_env/${ACCOUNT_ENV}.env

# Run Fastlane
cd delivery
bundle exec fastlane ios deploy \
  app_dir:../output/ios/${APP_SLUG} \
  bundle_id:${BUNDLE_ID} \
  scheme:${SCHEME}

# Update state
python3 ../brain/update_app_status.py ${APP_SLUG} "submitted"
```

### Delivery Pipeline Flow

```
Factory drops project to output/ios/{app}/
    │
    ▼
delivery/scripts/deploy_ios.sh triggered
    │
    ├── fastlane match (auto-sign)
    ├── fastlane gym (build .ipa)
    ├── fastlane snapshot (generate screenshots) [optional]
    ├── fastlane frameit (add device frames)
    ├── fastlane deliver (upload to App Store Connect)
    │
    ▼
App appears in App Store Connect
    │
    ▼
[HUMAN GATE] Review metadata → click "Submit for Review"
    │
    ▼
Apple review (1-3 days)
    │
    ├── APPROVED → brain updates status → live
    └── REJECTED → brain reads reason → factory fixes → re-deploy
```

### What Delivery Automates (vs. what remains manual)

| Step | Automated by Fastlane | Still Manual |
|------|----------------------|--------------|
| Code signing | ✅ match | One-time cert setup |
| Building .ipa/.aab | ✅ gym/gradle | — |
| Screenshot generation | ✅ snapshot | — |
| Device frames on screenshots | ✅ frameit | — |
| Metadata upload (title, desc, keywords) | ✅ deliver/supply | — |
| Binary upload | ✅ deliver/supply | — |
| Submit for review | ⚠️ Can be automated | Recommend human approval |
| Handle rejections | ❌ | Human reads, triggers fix |

---

## 9. Layer 4: Human Gate (5%)

Reduced from v1 thanks to Fastlane automation:

### One-Time Setup [HUMAN GATE]
1. Create 6 iOS + 6 Android developer accounts
2. Generate App Store Connect API key per iOS account
3. Set up Google Play service account JSON per Android account
4. Run `fastlane match init` to set up code signing repo
5. Store all credentials in `config/fastlane_env/`

### Per-App (After Fastlane Upload) [HUMAN GATE]
1. Open App Store Connect / Google Play Console
2. Verify metadata looks correct (title, screenshots, price)
3. Click "Submit for Review" (iOS) or "Submit" (Android)
4. Handle rejections if any

---

## 10–12. Market Intelligence, Scoring, and 20 Utility Ideas

*Identical to v1 instruction book sections 8-10. All 20 pre-scored app ideas are retained. Refer to v1 for full details.*

Key data points:
- ranks.csv: 800,577 rows, 174 countries, 42 genres, 12,258 unique paid apps
- Top markets: US ($140/user/yr), Japan (highest per capita), UK, Australia, Canada
- Blueprint apps: AutoSleep (159 countries), Shadowrocket (156), AnkiMobile (155)
- 15% Apple commission under Small Business Program

---

## 13. Custom High-Value App Ideas

These are YOUR strategic app ideas. They break the "zero server" rule because they have higher revenue ceilings. Budget a small server cost ONLY for these — keep it under $10/month total.

### Custom App 1: Global Bidding Hub

**Concept:** Aggregator of global tender/bidding/procurement opportunities. Scrape public tender databases, package by country/industry, sell access as a paid app.

**Why it works:**
- Tender aggregator services charge $50-500/month for subscriptions
- A $4.99–$9.99 paid app with bundled data is a bargain by comparison
- Government procurement is 15% of national budgets globally — huge market
- Data sources are PUBLIC (government procurement portals, World Bank, UN, ADB)
- Business users have high willingness-to-pay

**Architecture:**
```
Data layer (server, ~$5/month):
├── Scraper: Python scripts on a $5/mo VPS (DigitalOcean/Vultr)
│   ├── Scrapes public procurement portals daily
│   ├── Structures: title, deadline, country, sector, value, source URL
│   └── Outputs: tenders.json (bundled into app update weekly)
│
App layer (on-device):
├── Browse tenders by country, sector, deadline
├── Search and filter
├── Save favorites / set alerts (local notifications)
├── Offline access (all data bundled)
└── Weekly app updates push new tender data
```

**Pricing:** Tier 5 ($4.99) or Tier 10 ($9.99)
**Target markets:** All 175 countries (business users everywhere)
**Languages:** English, Chinese, Arabic, Spanish, French (top procurement markets)
**Competitive advantage:** No good mobile-native tender app exists at a one-time purchase price. All competitors are subscription web services.

### Custom App 2: LLM Token Wallet

**Concept:** A mobile app that lets users buy and manage AI/LLM API tokens. You buy Chinese LLM tokens in bulk (DeepSeek, Qwen, GLM, Kimi) at their ultra-low Chinese prices, and resell to international users at a markup — still far cheaper than OpenAI/Anthropic.

**Why it works:**
- Chinese LLM tokens cost 5-30× less than Western equivalents
- DeepSeek V4 Flash: $0.14/M input tokens vs Claude Opus: $15/M
- International developers WANT access but face payment/access friction
- You're solving an arbitrage + access problem simultaneously
- Gateway services like chinawhapi.com already prove this market exists

**Architecture:**
```
Backend (lightweight, ~$5/month):
├── Token balance API (simple REST on $5 VPS)
├── Integrates with: DeepSeek API, Qwen API, GLM API, Kimi API
├── User buys token packs via in-app purchase
├── App stores token balance, routes API calls through your gateway
└── Your margin: buy at Chinese price, sell at 2-3x (still 5-10x cheaper than OpenAI)

App layer:
├── Token balance dashboard
├── Buy token packs ($0.99 = 1M tokens, $4.99 = 10M tokens, etc.)
├── API key management (user gets a key to use in their apps)
├── Usage analytics
├── Model comparison (DeepSeek vs Qwen vs GLM benchmarks)
└── Playground: test prompts against different models
```

**Pricing model:** In-app purchases for token packs (not paid download)
- This is an EXCEPTION to the "paid download only" rule
- IAP allows recurring revenue and higher lifetime value
- Apple takes 15% of IAP too (Small Business Program)

**Revenue math:**
```
Buy: DeepSeek V4 Flash at $0.14/M input tokens
Sell: $0.99 for 2M tokens (effective $0.50/M)
Your margin: $0.50 - $0.14 = $0.36/M tokens
After Apple's 15%: $0.42 net per $0.99 pack
If 100 users buy 4 packs/month: $168/month pure margin
```

**Target markets:** US, Europe, Japan, Korea, Southeast Asia — developers who want cheap AI but can't easily pay Chinese providers
**Languages:** English, Japanese, Korean (developer markets)

### Custom App 3: LLM Token Marketplace (Expansion of App 2)

**Concept:** Expand the wallet into a full marketplace. Users can:
- Compare prices across all Chinese LLM providers
- Route requests to the cheapest model for their use case
- Auto-switch between models based on task type
- Community ratings on model quality per task

**This is the $10K+/month ceiling app** — start with the simple wallet, expand if it gains traction.

### Custom App Integration Rules

| Rule | Standard Apps | Custom Apps |
|------|--------------|-------------|
| Server allowed | ❌ Never | ✅ Max $10/mo total |
| Networking code | ❌ Never | ✅ Required |
| In-app purchases | ❌ Paid download only | ✅ Allowed for token packs |
| Third-party APIs | ❌ Never | ✅ LLM provider APIs |
| Build complexity | 2-12 hours | 40-80 hours |
| Account allocation | ios_001 through ios_004 | ios_005 dedicated |
| Priority | Ship first (volume) | Ship in month 2 (after pipeline proven) |

---

## 14. Pricing Strategy by Country

### Standard Apps (Utilities/Health/Education)

| App Type | iOS Tier | USD | Strategy |
|----------|----------|-----|----------|
| Simple utility | Tier 1 | $0.99 | Impulse buy, volume play |
| Sensor-based tool | Tier 2 | $1.99 | Hardware = perceived value |
| Education/Reference | Tier 2-3 | $1.99-$2.99 | Students pay for study tools |
| Health/Fitness | Tier 2 | $1.99 | Health = willingness to pay |
| Photo/Creative | Tier 3 | $2.99 | Professionals pay more |
| Complex apps | Tier 3-5 | $2.99-$4.99 | Higher effort = higher price |

### Custom Apps

| App | iOS Price | Android Price | IAP |
|-----|-----------|--------------|-----|
| Global Bidding Hub | $4.99-$9.99 | $4.99-$9.99 | None |
| LLM Token Wallet | Free | Free | $0.99-$9.99 token packs |

---

## 15. ASO & Localization Strategy

### Localization Priority (by iOS revenue)

| Priority | Language | Markets | Revenue Share |
|----------|----------|---------|---------------|
| 1 | English | US, UK, AU, CA, NZ, SG, HK | 45% |
| 2 | Japanese | Japan | 15% |
| 3 | German | DE, AT, CH | 8% |
| 4 | Korean | South Korea | 5% |
| 5 | Simplified Chinese | China | 10% |
| 6 | French | FR, CA-FR, BE | 4% |
| 7 | Spanish | ES, MX, Latin America | 4% |
| 8 | Portuguese | BR, PT | 3% |
| 9 | Traditional Chinese | TW, HK | 2% |
| 10 | Arabic | UAE, SA, EG | 2% |

### Phased Rollout
- **Weeks 1-2:** English only (ship fast)
- **Weeks 3-4:** Add Japanese + German for top performers
- **Month 2:** Korean, Chinese for all apps
- **Month 3+:** Full 10-language for winners

---

## 16. Account Management

### accounts.json Initial State

```json
{
  "accounts": [
    {"id": "ios_001", "platform": "ios", "cost": 99, "status": "active", "focus": "Utilities+Productivity", "apps": [], "total_earned": 0},
    {"id": "ios_002", "platform": "ios", "cost": 99, "status": "active", "focus": "Health+Fitness", "apps": [], "total_earned": 0},
    {"id": "ios_003", "platform": "ios", "cost": 99, "status": "active", "focus": "Education+Reference", "apps": [], "total_earned": 0},
    {"id": "ios_004", "platform": "ios", "cost": 99, "status": "active", "focus": "Photography+Creative", "apps": [], "total_earned": 0},
    {"id": "ios_005", "platform": "ios", "cost": 99, "status": "active", "focus": "Custom Apps", "apps": [], "total_earned": 0},
    {"id": "ios_006", "platform": "ios", "cost": 99, "status": "active", "focus": "Reserve/Overflow", "apps": [], "total_earned": 0},
    {"id": "android_001", "platform": "android", "cost": 25, "status": "active", "focus": "Mirror Utilities", "apps": [], "total_earned": 0},
    {"id": "android_002", "platform": "android", "cost": 25, "status": "active", "focus": "Mirror Health+Edu", "apps": [], "total_earned": 0},
    {"id": "android_003", "platform": "android", "cost": 25, "status": "active", "focus": "Mirror Photo+Creative", "apps": [], "total_earned": 0},
    {"id": "android_004", "platform": "android", "cost": 25, "status": "active", "focus": "Custom Apps", "apps": [], "total_earned": 0},
    {"id": "android_005", "platform": "android", "cost": 25, "status": "active", "focus": "Reserve", "apps": [], "total_earned": 0},
    {"id": "android_006", "platform": "android", "cost": 25, "status": "active", "focus": "Reserve", "apps": [], "total_earned": 0}
  ],
  "total_invested": 800,
  "reserve_fund": 56
}
```

---

## 17. The Sleepless Loop

```
BRAIN (every 30 min):
  Load state → Check revenue → Kill/boost → Refill queue → Save state

FACTORY (continuous):
  Check queue/pending/ → Build → Output to output/{platform}/{app}/ → Repeat

DELIVERY (triggered per app):
  Detect new project in output/ → fastlane build+sign+upload → Update state

All state on disk. Crash-safe. Restartable. Parallel.
```

---

## 18. Parallel Execution

```
Factory Worker A: Building ios/unit_converter_pro
Factory Worker B: Building android/unit_converter_pro
Factory Worker C: Building ios/sound_level_meter
Delivery Worker:  Uploading ios/tip_calculator_deluxe to App Store

ALL RUNNING SIMULTANEOUSLY. No blocking.
Brain refills queue on its own 30-min cycle.
```

---

## 19. Risk Management

| Risk | Level | Mitigation |
|------|-------|------------|
| Apple account ban for spam | HIGH | Space 2-3 days between submissions per account. Unique UI per app. Category-focused accounts |
| App review rejection (~40%) | MEDIUM | Pre-validate against guidelines. Budget 1-2 resubmissions. Fastlane precheck |
| Near-zero downloads | MEDIUM | Ruthless ASO. 10-language localization. Cross-promote between own apps |
| Associated accounts flagged | MEDIUM | Each account legitimately separate. All share $1M threshold |
| Custom app server costs | LOW | Cap at $10/mo. Kill if ROI negative after 60 days |
| LLM token pricing changes | LOW | Monitor Chinese provider prices weekly. Adjust margins |

---

## 20. Pipeline Launch Manifest (First 24 Apps)

This is the pre-loaded build queue. The brain agent executes this list in order without further analysis. Every decision is already made: what to build, which platform, which account, which price, which countries, which languages.

### Phase 1: Quick wins (week 1–2) — Prove the pipeline

| # | App name | Category | Platform | iOS acct | And acct | Price | Target countries | Languages | Hours |
|---|----------|----------|----------|----------|----------|-------|-----------------|-----------|-------|
| 1 | Tip calculator deluxe | Utilities | Both | ios_001 | and_001 | $0.99 | US, CA, GB, AU, AE, SG | EN | 2h |
| 2 | Unit converter pro | Utilities | Both | ios_001 | and_001 | $0.99 | All 175 (universal) | EN, JA, DE | 3h |
| 3 | Sound level meter | Utilities | iOS | ios_001 | — | $1.99 | US, GB, DE, JP, AU, CA, FR | EN, JA, DE | 4h |
| 4 | QR barcode scanner+ | Utilities | Both | ios_001 | and_001 | $0.99 | All 175 (universal) | EN | 4h |
| 5 | Pomodoro focus timer | Productivity | Both | ios_001 | and_001 | $1.99 | US, GB, JP, KR, DE, BR, IN | EN, JA | 4h |
| 6 | Screen ruler & measure | Utilities | iOS | ios_001 | — | $1.99 | US, GB, DE, FR, JP, AU | EN, DE | 5h |
| 7 | Color picker & palette | Photo | iOS | ios_004 | — | $1.99 | US, GB, DE, JP, KR, FR | EN | 5h |
| 8 | Morse code translator | Education | Both | ios_003 | and_002 | $0.99 | US, GB, AU, CA, DE | EN | 4h |

### Phase 2: Health + education (week 3–4) — Higher perceived value

| # | App name | Category | Platform | iOS acct | And acct | Price | Target countries | Languages | Hours |
|---|----------|----------|----------|----------|----------|-------|-----------------|-----------|-------|
| 9 | BMI & body fat calc | Health | Both | ios_002 | and_002 | $0.99 | US, GB, DE, JP, AU, BR, IN | EN, JA | 5h |
| 10 | Breathing exercise timer | Health | Both | ios_002 | and_002 | $1.99 | US, GB, DE, FR, JP, AU, CA | EN, JA, DE | 5h |
| 11 | Water intake tracker | Health | Both | ios_002 | and_002 | $1.99 | US, GB, DE, JP, AU, CA, BR | EN, JA | 5h |
| 12 | White noise sleep sounds | Health | Both | ios_002 | and_002 | $2.99 | US, GB, JP, KR, DE, AU, CA, FR | EN | 6h |
| 13 | Flashcard study deck | Education | Both | ios_003 | and_002 | $2.99 | US, GB, DE, JP, KR, FR, BR, IN | EN, JA, KO | 8h |
| 14 | Periodic table explorer | Education | Both | ios_003 | and_002 | $1.99 | US, GB, DE, JP, KR, FR, IN, BR | EN, JA | 8h |
| 15 | Day counter & countdown | Lifestyle | Both | ios_001 | and_001 | $0.99 | US, GB, JP, KR, DE, AU, CA | EN, JA, KO | 6h |
| 16 | Habit streak tracker | Productivity | Both | ios_001 | and_001 | $2.99 | US, GB, DE, JP, KR, FR, AU, BR | EN, JA, DE | 8h |

### Phase 3: Creative + advanced (week 5–6) — Higher price ceiling

| # | App name | Category | Platform | iOS acct | And acct | Price | Target countries | Languages | Hours |
|---|----------|----------|----------|----------|----------|-------|-----------------|-----------|-------|
| 17 | Photo resizer & compress | Photo | Both | ios_004 | and_003 | $1.99 | US, GB, JP, DE, IN, BR | EN, JA | 5h |
| 18 | EXIF photo viewer | Photo | iOS | ios_004 | — | $1.99 | US, GB, DE, JP, AU, CA | EN, DE | 6h |
| 19 | Guitar tuner | Music | iOS | ios_004 | — | $1.99 | US, GB, DE, FR, JP, BR, MX | EN | 8h |
| 20 | Pixel art maker | Creative | Both | ios_004 | and_003 | $2.99 | US, GB, JP, KR, DE, FR | EN, JA | 12h |

### Phase 4: Custom high-value apps (week 5–8) — Strategic bets

| # | App name | Category | Platform | iOS acct | And acct | Price | Target countries | Languages | Hours |
|---|----------|----------|----------|----------|----------|-------|-----------------|-----------|-------|
| 21 | Global bidding hub | Custom | Both | ios_005 | and_004 | $4.99 | All 175 (biz global) | EN, ZH, AR, ES, FR | 40h |
| 22 | LLM token wallet | Custom | Both | ios_005 | and_004 | Free+IAP | US, GB, DE, JP, KR, SG, NL | EN, JA, KO | 60h |
| 23 | LLM model compare | Custom | Both | ios_005 | and_004 | $2.99 | US, GB, DE, JP, KR, IN, SG | EN, JA | 20h |
| 24 | CN token reseller API | Custom | Android | — | and_004 | Free+IAP | Global dev markets | EN, ZH-Hans | 30h |

### Account distribution

| Account | Focus | Apps assigned | Status |
|---------|-------|--------------|--------|
| ios_001 | Utilities + Productivity | #1-6, #15-16 (8 apps) | Active from day 1 |
| ios_002 | Health + Fitness | #9-12 (4 apps) | Active from day 1 |
| ios_003 | Education + Reference | #8, #13-14 (3 apps) | Active from day 1 |
| ios_004 | Photo + Creative + Music | #7, #17-20 (5 apps) | Active from day 1 |
| ios_005 | Custom high-value | #21-23 (3 apps) | Active from week 5 |
| ios_006 | Reserve / overflow | 0 apps | Held for week 9+ |
| and_001 | Mirror Utilities | #1-2, #4-5, #15-16 (6 apps) | Active from day 1 |
| and_002 | Mirror Health + Edu | #8-14 (7 apps) | Active from day 1 |
| and_003 | Mirror Photo + Creative | #17, #20 (2 apps) | Active from week 5 |
| and_004 | Custom apps | #21-24 (4 apps) | Active from week 5 |
| and_005 | Reserve | 0 apps | Held |
| and_006 | Reserve | 0 apps | Held |

### Platform routing rationale

- **Both** (16 apps): Universal logic, no hardware-specific APIs. Double reach at minimal extra build cost.
- **iOS only** (4 apps): #3 (CoreMotion accelerometer), #6 (CoreMotion gyroscope), #7 (CoreImage camera pipeline), #18 (PhotoKit metadata), #19 (AVAudioEngine FFT) — these use iOS-specific sensor APIs that don't translate 1:1 to Android. Port later if revenue justifies the effort.
- **Android only** (1 app): #24 — Google Play has a larger developer audience in emerging markets where cheap LLM tokens have the most appeal.

### Language phasing rationale

- **EN only** (week 1-2): Ship fast, get market signal
- **EN + JA** (week 2-3): Japan is #2 iOS revenue market globally, highest spend per capita
- **EN + JA + DE** (week 3-4): Germany is #3 in Europe, fewer devs bother with German ASO = less competition
- **EN + JA + KO** (education apps): South Korean students are heavy paid app buyers
- **EN + ZH + AR + ES + FR** (bidding hub): Top 5 government procurement languages globally

---

## 21. Week-by-Week Execution Plan

### Month 1: Foundation + Pipeline

| Week | iOS Apps | Android Apps | Focus |
|------|----------|-------------|-------|
| 1 | 5 utilities | 5 mirrors | Set up Fastlane, ship fastest apps |
| 2 | 5 productivity | 5 mirrors | A/B test pricing. First revenue |
| 3 | 5 health/education | 5 mirrors | Add Japanese localization for top 5 |
| 4 | 5 photo/creative | 5 mirrors | Begin Custom App 1 (Global Bidding Hub) |

### Month 2: Scale + Custom Apps

| Week | iOS Apps | Android Apps | Focus |
|------|----------|-------------|-------|
| 5-6 | 10 new + localize top 10 | 10 mirrors | Ship Global Bidding Hub. Start Token Wallet |
| 7-8 | 10 new | 10 mirrors | Ship Token Wallet. Full 10-language localization |

### Month 3-5: Compound

| Month | Total Apps | Revenue Target | Focus |
|-------|-----------|---------------|-------|
| 3 | 120+ iOS, 80+ Android | $800 breakeven | Double down on winners. Kill losers |
| 4 | 160+ iOS, 120+ Android | $1500+ | Custom apps generating recurring IAP revenue |
| 5 | 200+ total | $3000+/month | System fully autonomous. Evaluate Mac App Store |

---

## 22. File Specifications

### spec.json (Brain → Factory)

```json
{
  "spec_version": "2.0",
  "app_name": "Unit Converter Pro",
  "slug": "unitconverterpro",
  "bundle_id": "com.appfactory.unitconverterpro",
  "category": "Utilities",
  "platform": "both",
  "description": "All-in-one unit converter with 50+ unit types",
  "features": ["50+ units", "favorites", "history", "search"],
  "template": "utility_template",
  "ios_frameworks": ["SwiftUI"],
  "android_frameworks": ["Jetpack Compose"],
  "price_tier": 1,
  "price_usd": 0.99,
  "target_countries": ["us", "gb", "au", "ca", "de", "fr", "jp"],
  "languages": ["en", "ja", "de"],
  "keywords": ["unit converter", "metric converter"],
  "ios_account": "ios_001",
  "android_account": "android_001",
  "requires_server": false,
  "estimated_build_hours": 3,
  "score": 42.5,
  "created_at": "2026-05-21T10:00:00Z",
  "status": "pending"
}
```

---

## 23. Claude Code Execution Rules

### Full Autonomy To:
- Decide what to build (via scoring)
- Write all Swift/Kotlin code
- Generate all metadata, icons, screenshots
- Write Fastlane configuration per app
- Make pricing and localization decisions
- Manage 12 accounts and distribute apps
- Kill underperformers, boost winners
- Execute delivery pipeline

### No Permission Needed For:
- ANY coding decision
- ANY market analysis
- ANY pricing decision
- ANY localization decision
- ANY build queue decision
- Running Fastlane build/upload commands
- Generating new app ideas beyond the initial 20

### Does NOT Have Permission To:
- Spend money beyond the $800 budget
- Create additional developer accounts without revenue justification
- Exceed $10/month in server costs for custom apps
- Submit apps for review (that's the 5% human gate)
- Make legal judgments (trademark, copyright)

### Execution Order

```
Phase 0: Setup (Day 1)
  1. Create folder structure (Section 4)
  2. Implement brain.py + all modules
  3. Implement factory.py + all templates
  4. Set up Fastlane configuration
  5. Initialize state files for all 12 accounts

Phase 1: First Blood (Days 2-7)
  6. Brain analyzes ranks.csv → generates first 5 specs
  7. Factory builds 5 iOS apps + 5 Android mirrors
  8. Delivery system uploads all 10 to stores
  9. [HUMAN GATE] Approve submissions

Phase 2: Velocity (Days 8-30)
  10. Brain runs on 30-min cycle
  11. Factory runs continuously
  12. Delivery triggers automatically per completed app
  13. Target: 40 iOS + 40 Android apps live by day 30

Phase 3: Custom Apps (Days 15-45)
  14. Begin Global Bidding Hub development
  15. Begin LLM Token Wallet development
  16. Set up lightweight VPS ($10/mo max) for custom app backends

Phase 4: Compound (Days 30+)
  17. Localize winners into 10 languages
  18. Kill apps with $0 revenue after 30 days
  19. System runs autonomously

NO FURTHER PERMISSION NEEDED. START BUILDING.
```
