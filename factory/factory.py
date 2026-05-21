"""Factory queue manager (Layer 2).

The factory does not itself generate Swift/Kotlin source — that is the job of
a Claude Code worker session. The factory's job is everything around the
codegen: claiming a spec, scaffolding an isolated workspace, tracking status,
and moving the workspace through the queue.

Lifecycle:
    python -m factory.factory claim
        -> pops the next pending spec, creates workspaces/ws_XXX_slug/,
           copies spec.json, writes workspace.json + status.json,
           moves the spec pending -> building, prints the workspace path.
        -> a Claude Code worker then fills ios/, android/, shared/.

    python -m factory.factory complete ws_XXX
        -> writes result.json, moves building -> built.

    python -m factory.factory status
        -> prints a one-line summary of every queue bucket.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

# Allow "python -m factory.factory" and "python factory/factory.py" both.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brain import state_io  # noqa: E402
from brain.account_manager import normalize_account_id  # noqa: E402


def _load_spec(spec_rel_path: str) -> dict:
    path = os.path.join(state_io.ROOT, spec_rel_path)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def claim() -> str | None:
    """Claim the next pending spec and scaffold its workspace.

    Returns the workspace path, or None if the queue is empty.
    """
    queue = state_io.load_state("queue")
    if not queue["pending"]:
        print("queue/pending is empty — nothing to claim")
        return None

    entry = queue["pending"][0]
    spec = _load_spec(entry["spec"])
    ws_id = spec["workspace_id"]
    slug = spec["slug"]
    ws_name = f"{ws_id}_{slug}"
    ws_path = os.path.join(state_io.WORKSPACES_DIR, ws_name)

    _scaffold_workspace(ws_path, spec)

    # Move pending -> building.
    queue["pending"] = queue["pending"][1:]
    queue.setdefault("building", []).append({
        "workspace_id": ws_id, "slug": slug, "workspace": ws_name,
    })
    state_io.save_state("queue", queue)
    _record_build_event(ws_id, "claimed")

    print(ws_path)
    return ws_path


def _scaffold_workspace(ws_path: str, spec: dict) -> None:
    """Create the isolated workspace skeleton for one app."""
    platforms = spec.get("platforms", ["ios"])
    for sub in ("shared",):
        os.makedirs(os.path.join(ws_path, sub), exist_ok=True)
    if "ios" in platforms:
        os.makedirs(os.path.join(ws_path, "ios"), exist_ok=True)
    if "android" in platforms:
        os.makedirs(os.path.join(ws_path, "android"), exist_ok=True)

    # Read-only copy of the spec for the worker and the audit trail.
    state_io.save_json(os.path.join(ws_path, "spec.json"), spec)

    ios_account = normalize_account_id(spec.get("ios_account"))
    android_account = normalize_account_id(spec.get("android_account"))

    workspace = {
        "workspace_id": spec["workspace_id"],
        "app_slug": spec["slug"],
        "app_name": spec["app_name"],
        "bundle_id_ios": spec.get("bundle_id_ios"),
        "bundle_id_android": spec.get("bundle_id_android"),
        "ios_account": ios_account,
        "android_account": android_account,
        "platforms": platforms,
        "created_at": state_io.now_iso(),
        "status": "building",
        "pipeline_stage": "factory",
        "build_history": [
            {"stage": "spec_created", "at": spec.get("created_at", state_io.now_iso())},
            {"stage": "factory_started", "at": state_io.now_iso()},
        ],
    }
    state_io.save_json(os.path.join(ws_path, "workspace.json"), workspace)

    blank = {"code": "pending", "build": "pending", "sign": "pending",
             "upload": "pending", "review": "pending", "live": False}
    status = {"workspace_id": spec["workspace_id"]}
    if "ios" in platforms:
        status["ios"] = dict(blank)
    if "android" in platforms:
        status["android"] = dict(blank)
    state_io.save_json(os.path.join(ws_path, "status.json"), status)


def complete(workspace_id: str) -> None:
    """Mark a workspace's code generation done; move building -> built."""
    queue = state_io.load_state("queue")
    item = None
    remaining = []
    for entry in queue.get("building", []):
        if entry.get("workspace_id") == workspace_id:
            item = entry
        else:
            remaining.append(entry)
    queue["building"] = remaining
    if item is None:
        item = {"workspace_id": workspace_id}
    queue.setdefault("built", []).append(item)
    state_io.save_state("queue", queue)

    ws_dir = _find_workspace_dir(workspace_id)
    if ws_dir:
        result = {
            "workspace_id": workspace_id,
            "built_at": state_io.now_iso(),
            "result": "success",
            "code_generated_by": "claude-code-worker",
        }
        state_io.save_json(os.path.join(ws_dir, "result.json"), result)
        status_path = os.path.join(ws_dir, "status.json")
        if os.path.exists(status_path):
            status = state_io.load_json(status_path)
            for plat in ("ios", "android"):
                if plat in status:
                    status[plat]["code"] = "complete"
            state_io.save_json(status_path, status)

    apps = state_io.load_state("apps")
    for app in apps["apps"]:
        if app["workspace_id"] == workspace_id:
            app["status"] = "built"
            app["pipeline_stage"] = "built"
            break
    state_io.save_state("apps", apps)

    state = state_io.load_state("state")
    state["counters"]["apps_built"] = state["counters"].get("apps_built", 0) + 1
    state_io.save_state("state", state)
    _record_build_event(workspace_id, "built")
    print(f"{workspace_id} -> built")


def _find_workspace_dir(workspace_id: str) -> str | None:
    if not os.path.isdir(state_io.WORKSPACES_DIR):
        return None
    for name in os.listdir(state_io.WORKSPACES_DIR):
        if name.startswith(workspace_id + "_"):
            return os.path.join(state_io.WORKSPACES_DIR, name)
    return None


def _record_build_event(workspace_id: str, event: str) -> None:
    log = state_io.load_state("build_log")
    log["builds"].append({
        "workspace_id": workspace_id,
        "event": event,
        "at": state_io.now_iso(),
    })
    state_io.save_state("build_log", log)


def status() -> None:
    queue = state_io.load_state("queue")
    for bucket in ("pending", "building", "built", "delivering",
                   "submitted", "live", "failed"):
        ids = [e.get("workspace_id") for e in queue.get(bucket, [])]
        print(f"{bucket:11s}: {len(ids):2d}  {', '.join(ids)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="App Factory queue manager")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("claim", help="claim next pending spec, scaffold workspace")
    c = sub.add_parser("complete", help="mark a workspace's codegen complete")
    c.add_argument("workspace_id")
    sub.add_parser("status", help="print queue bucket summary")
    args = parser.parse_args()

    if args.cmd == "claim":
        claim()
    elif args.cmd == "complete":
        complete(args.workspace_id)
    elif args.cmd == "status":
        status()


if __name__ == "__main__":
    main()
