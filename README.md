# App Factory v2

An autonomous app-publishing business operating system. The brain decides what
to build, the factory builds it, the delivery layer ships it, and a thin human
gate approves store submissions. Built from
[`instructions/APP_FACTORY_INSTRUCTION_BOOK_V2.md`](instructions/APP_FACTORY_INSTRUCTION_BOOK_V2.md).

## Status

Phase 0 (setup) and Phase 1 (first 5 apps) are complete.

| Workspace | App | Platforms | Price | Stage |
|-----------|-----|-----------|-------|-------|
| ws_001 | Tip Calculator Deluxe | iOS + Android | $0.99 | built |
| ws_002 | Unit Converter Pro | iOS + Android | $0.99 | built |
| ws_003 | Sound Level Meter | iOS | $1.99 | built |
| ws_004 | QR & Barcode Scanner+ | iOS + Android | $0.99 | built |
| ws_005 | Pomodoro Focus Timer | iOS + Android | $1.99 | built |

All five workspaces hold complete, code-complete SwiftUI and Kotlin/Compose
projects. They are **not yet compiled** — the host is Windows; building iOS
needs a Mac + Xcode 16 and Android needs Android Studio. See each workspace's
`shared/README.md` for per-app build notes.

## Architecture

```
LAYER 1  brain/      Strategic decision engine — what/where/price/platform
LAYER 2  factory/    Spec -> isolated app workspace (Claude Code is the worker)
LAYER 3  delivery/   Fastlane build + sign + upload to the stores
LAYER 4  [human]     Approve the final "Submit for Review" click
```

The build queue flows `pending -> building -> built -> delivering ->
submitted -> live`. Each app is a self-contained workspace under
`workspaces/` with zero dependencies on any other app (see instruction book
section 5, "Workspace Isolation").

## Layout

```
brain/        Layer 1 — orchestrator + decision modules (Python, stdlib only)
factory/      Layer 2 — queue manager + workspace scaffolding
delivery/     Layer 3 — Fastlane Fastfile / Matchfile / scripts / CI workflows
workspaces/   One self-contained universe per app (ws_NNN_slug/)
state/        Persistent JSON state — crash-safe, restartable
queue/        pending/ building/ built/ ... spec hand-off folders
config/       config.yaml, price tiers, genre map, fastlane credentials
data/         Market intelligence (ranks.csv goes here)
scripts/      setup + run wrappers (.sh and .ps1)
docs/         Operations guide
instructions/ The source instruction book + the 5 original specs
```

## Operating it

```bash
# Check the toolchain
bash scripts/setup.sh

# Run one brain cycle (revenue -> kill/boost -> account health -> queue refill)
python -m brain.brain --once          # or: scripts/run_brain.ps1 --once

# Inspect the build queue
python -m factory.factory status

# Claim the next spec -> scaffolds a workspace for a Claude Code worker
python -m factory.factory claim

# After a worker generates code in the workspace
python -m factory.factory complete ws_006

# Ship everything in queue/built (macOS)
bash scripts/run_delivery.sh
```

The brain and factory run on any OS with Python 3.11+ and need **no
third-party packages**. The delivery layer needs macOS, Xcode, Ruby + Fastlane.

## Building from Windows

iOS apps cannot be compiled on Windows. Use GitHub Actions' hosted macOS
runners — `.github/workflows/ios_deploy.yml` builds, signs, and uploads with
no Mac required. Android builds locally in Android Studio, or on free Linux
runners via `.github/workflows/android_deploy.yml`. Full setup:
[docs/GITHUB_ACTIONS_SETUP.md](docs/GITHUB_ACTIONS_SETUP.md).

## Human gate (the 5%)

1. **Once** — create the 12 developer accounts, generate API keys, fill
   `config/fastlane_env/` (see its `README.md`), run `scripts/setup_fastlane.sh`.
2. **Per app** — after Fastlane uploads, review the metadata in App Store
   Connect / Play Console and click *Submit for Review*.
3. **If rejected** — read the reason, trigger a factory fix, re-deploy.

## Budget

$800 seed: 6 iOS accounts ($594) + 6 Android accounts ($150) + $56 reserve.
Tracked live in `state/state.json` and `state/accounts.json`.
