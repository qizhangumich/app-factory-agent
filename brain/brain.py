"""Brain orchestrator — the 30-minute strategic loop (Layer 1).

Each cycle the brain:
  1. loads state from disk
  2. refreshes revenue rollups
  3. runs the kill/boost engine
  4. checks account health
  5. refills the build queue if it is running low
  6. saves state and logs every decision with its reasoning

Run one cycle:   python -m brain.brain --once
Run forever:     python -m brain.brain         (sleeps 30 min between cycles)
"""
from __future__ import annotations

import argparse
import json
import os
import time

from . import (account_manager, app_scorer, kill_boost, localization_planner,
               market_scanner, platform_router, pricing_optimizer,
               revenue_tracker, state_io)

CYCLE_SECONDS = 30 * 60


def log_decision(cycle: int, dtype: str, decision: str, reasoning: str) -> None:
    """Append an entry to the brain's decision log."""
    doc = state_io.load_state("decisions")
    doc["decisions"].append({
        "at": state_io.now_iso(),
        "cycle": cycle,
        "type": dtype,
        "decision": decision,
        "reasoning": reasoning,
    })
    state_io.save_state("decisions", doc)


def generate_spec(idea: dict, workspace_id: str) -> str:
    """Turn a scored idea into a spec.json written to queue/pending/.

    Returns the path of the spec file.
    """
    routing = platform_router.route_platform(idea)
    platforms = (["ios", "android"] if routing["primary"] == "both"
                 else [routing["primary"]])
    pricing = pricing_optimizer.optimize(idea)
    languages = localization_planner.plan_languages(idea, phase="launch")

    ios_account = (account_manager.assign_account(idea["category"], "ios")
                   if "ios" in platforms else None)
    android_account = (account_manager.assign_account(idea["category"], "android")
                       if "android" in platforms else None)

    slug = idea["slug"]
    spec = {
        "spec_version": "2.1",
        "workspace_id": workspace_id,
        "app_name": idea["app_name"],
        "slug": slug,
        "bundle_id_ios": f"com.appfactory.{slug}",
        "bundle_id_android": f"com.appfactory.{slug}" if android_account else None,
        "category": idea["category"],
        "platforms": platforms,
        "ios_account": ios_account,
        "android_account": android_account,
        "template": idea.get("template", "utility_template"),
        "features": idea.get("features", []),
        "requires_server": idea.get("requires_server", False),
        "price_tier": pricing["price_tier"],
        "price_usd": pricing["price_usd"],
        "target_countries": idea.get("target_countries", "all_175"),
        "languages": languages,
        "estimated_build_hours": idea.get("estimated_build_hours", 8),
        "score": idea.get("score", app_scorer.score_idea(idea)["score"]),
        "created_at": state_io.now_iso(),
        "status": "pending",
    }
    path = os.path.join(state_io.QUEUE_DIR, "pending",
                        f"spec_{workspace_id}_{slug}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(spec, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return path


def refill_queue(cycle: int) -> int:
    """If pending work is low, scan the market and enqueue fresh specs.

    Returns the number of specs added.
    """
    queue = state_io.load_state("queue")
    threshold = queue.get("min_pending_threshold", 5)
    if len(queue["pending"]) >= threshold:
        return 0

    state = state_io.load_state("state")
    needed = threshold - len(queue["pending"])
    ideas = market_scanner.scan(limit=needed)
    added = 0

    for idea in ideas:
        ws_num = state["counters"]["next_workspace_id"]
        ws_id = f"ws_{ws_num:03d}"
        spec_path = generate_spec(idea, ws_id)
        queue["pending"].append({
            "workspace_id": ws_id,
            "slug": idea["slug"],
            "spec": os.path.relpath(spec_path, state_io.ROOT).replace("\\", "/"),
            "build_order": ws_num,
        })
        state["counters"]["next_workspace_id"] = ws_num + 1
        state["counters"]["apps_specced"] = state["counters"].get("apps_specced", 0) + 1
        added += 1
        log_decision(cycle, "spec_generated",
                     f"Queued {idea['app_name']} ({ws_id}) for build.",
                     f"Market scan scored it {idea.get('score')}; queue was below "
                     f"the {threshold}-spec refill threshold.")

    if added:
        state_io.save_state("queue", queue)
        state_io.save_state("state", state)
    return added


def run_cycle() -> dict:
    """Execute one brain cycle. Returns a summary dict."""
    state = state_io.load_state("state")
    cycle = state["brain_cycle_count"] + 1

    revenue = revenue_tracker.refresh()
    kb = kill_boost.run()
    frozen = account_manager.check_health()
    added = refill_queue(cycle)

    state = state_io.load_state("state")
    state["brain_cycle_count"] = cycle
    state["last_brain_run"] = state_io.now_iso()
    state_io.save_state("state", state)

    summary = {
        "cycle": cycle,
        "total_earned": revenue["total_earned"],
        "killed": kb["killed"],
        "boosted": kb["boosted"],
        "frozen_accounts": [c["account_id"] for c in frozen],
        "specs_added": added,
    }
    log_decision(cycle, "cycle_complete",
                 f"Cycle {cycle}: +{added} specs, {len(kb['killed'])} killed, "
                 f"{len(kb['boosted'])} boosted.",
                 f"Revenue ${revenue['total_earned']}. "
                 f"Breakeven reached: {revenue['breakeven_reached']}.")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="App Factory brain agent")
    parser.add_argument("--once", action="store_true",
                        help="run a single cycle and exit")
    args = parser.parse_args()

    while True:
        summary = run_cycle()
        print(json.dumps(summary, indent=2))
        if args.once:
            break
        time.sleep(CYCLE_SECONDS)


if __name__ == "__main__":
    main()
