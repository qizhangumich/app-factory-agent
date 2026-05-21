# App Factory v2 — Operations Guide

How to run the factory day to day. The strategy and rationale live in
[`../instructions/APP_FACTORY_INSTRUCTION_BOOK_V2.md`](../instructions/APP_FACTORY_INSTRUCTION_BOOK_V2.md);
this file is the runbook.

## The sleepless loop

```
BRAIN     every 30 min   load state -> revenue -> kill/boost -> account health -> refill queue
FACTORY   continuous     claim spec -> scaffold workspace -> Claude worker writes code -> complete
DELIVERY  per built app  fastlane build + sign + upload -> human submits
```

All state is on disk under `state/`. The system is crash-safe: kill it at any
point and re-run — every state write is atomic.

## Brain

```
python -m brain.brain --once     # single cycle
python -m brain.brain            # loop forever (30-min cycles)
```

Each cycle is logged with reasoning to `state/decisions.json`. The brain
refills `queue/pending/` from `brain/market_scanner.py` whenever pending work
drops below `min_pending_threshold` (5). It never writes app code.

Modules: `market_scanner`, `app_scorer`, `pricing_optimizer`,
`localization_planner`, `account_manager`, `platform_router`,
`revenue_tracker`, `kill_boost`. All pure-stdlib Python.

## Factory

The factory is a queue manager; **code generation is a Claude Code worker
session**, one per workspace, run inside the scaffolded directory.

```
python -m factory.factory claim            # pending[0] -> workspaces/ws_NNN_slug/
# ... run a Claude Code factory worker in that workspace ...
python -m factory.factory complete ws_NNN  # building -> built
python -m factory.factory status           # queue bucket summary
```

`claim` writes `spec.json`, `workspace.json`, and `status.json` into the new
workspace and moves the spec `pending -> building`. The worker fills `ios/`,
`android/`, and `shared/`. `complete` writes `result.json` and moves it to
`built`.

## Delivery (macOS only)

```
bash delivery/scripts/deploy_workspace.sh workspaces/ws_001_tipcalcdeluxe
bash scripts/run_delivery.sh               # every workspace in queue/built
```

`deploy_workspace.sh` reads `workspace.json` to learn which account owns the
app, sources `config/fastlane_env/<account>.env`, then runs the `ios deploy`
and `android deploy` lanes. Uploads land as drafts — the human submits.

GitHub Actions equivalents: `delivery/github_actions/{ios,android}_deploy.yml`.

## Pipeline status updates

`brain/update_workspace_status.py` keeps `queue.json`, `apps.json`,
`state.json`, and the per-workspace `status.json` / `workspace.json` in sync:

```
python -m brain.update_workspace_status ws_001 submitted
python -m brain.update_workspace_status ws_001 live --platform ios
```

## Revenue

`scripts/update_revenue.sh` pulls store sales reports. Each sale is folded in
with `brain.revenue_tracker.record_revenue(workspace_id, account_id, usd, day)`,
which updates `revenue.json`, `accounts.json`, and `apps.json`. The next brain
cycle picks up the new numbers for kill/boost decisions.

## Decision rules (enforced by the brain)

| Trigger | Action |
|---|---|
| pending queue < 5 | scan market, score ideas, generate specs |
| app live ≥ 30 days, $0 revenue | kill it |
| app earns ≥ $10 in week 1 | flag for localization expansion |
| account $0 for 60 days | freeze, route new apps to overflow |
| reserve fund < $50 | pause new account creation |

## Adding a new app by hand

1. Drop a `spec.json` (schema: instruction book section 22) into `queue/pending/`
   and add it to `queue.json`'s `pending` list.
2. `python -m factory.factory claim`
3. Run a Claude Code factory worker in the new workspace.
4. `python -m factory.factory complete ws_NNN`
5. Deploy on macOS.
