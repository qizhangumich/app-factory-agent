"""Pipeline status updater — called by the factory and delivery layers.

Moves a workspace between pipeline stages, keeping queue.json, apps.json,
state.json, the workspace's own status.json/workspace.json, and the
queue/<stage>/ folders all consistent.

Usage:
    python -m brain.update_workspace_status ws_001 built
    python -m brain.update_workspace_status ws_001 live --platform ios
"""
from __future__ import annotations

import argparse
import os

from . import state_io

STAGES = ["pending", "building", "built", "delivering",
          "submitted", "live", "failed"]


def update(workspace_id: str, stage: str, platform: str | None = None) -> None:
    if stage not in STAGES:
        raise ValueError(f"unknown stage '{stage}', expected one of {STAGES}")

    _move_in_queue(workspace_id, stage)
    _update_apps(workspace_id, stage)
    _update_counters(stage)
    _update_workspace_files(workspace_id, stage, platform)


def _move_in_queue(workspace_id: str, stage: str) -> None:
    queue = state_io.load_state("queue")
    item = None
    for bucket in STAGES:
        kept = []
        for entry in queue.get(bucket, []):
            if entry.get("workspace_id") == workspace_id:
                item = entry
            else:
                kept.append(entry)
        queue[bucket] = kept
    if item is None:
        item = {"workspace_id": workspace_id}
    queue.setdefault(stage, []).append(item)
    state_io.save_state("queue", queue)


def _update_apps(workspace_id: str, stage: str) -> None:
    apps = state_io.load_state("apps")
    for app in apps["apps"]:
        if app["workspace_id"] == workspace_id:
            app["pipeline_stage"] = stage
            if stage == "built":
                app["status"] = "built"
            elif stage == "submitted":
                app["status"] = "submitted"
            elif stage == "live":
                app["status"] = "live"
                app["live_at"] = app.get("live_at") or state_io.now_iso()
            elif stage == "failed":
                app["status"] = "failed"
            break
    state_io.save_state("apps", apps)


def _update_counters(stage: str) -> None:
    state = state_io.load_state("state")
    counters = state["counters"]
    if stage == "built":
        counters["apps_built"] = counters.get("apps_built", 0) + 1
    elif stage == "submitted":
        counters["apps_submitted"] = counters.get("apps_submitted", 0) + 1
    elif stage == "live":
        counters["apps_live"] = counters.get("apps_live", 0) + 1
    state_io.save_state("state", state)


def _update_workspace_files(workspace_id: str, stage: str,
                            platform: str | None) -> None:
    ws_dir = _find_workspace_dir(workspace_id)
    if ws_dir is None:
        return

    ws_json = os.path.join(ws_dir, "workspace.json")
    if os.path.exists(ws_json):
        doc = state_io.load_json(ws_json)
        doc["pipeline_stage"] = stage
        doc.setdefault("build_history", []).append(
            {"stage": stage, "at": state_io.now_iso()})
        state_io.save_json(ws_json, doc)

    status_json = os.path.join(ws_dir, "status.json")
    if os.path.exists(status_json) and platform:
        doc = state_io.load_json(status_json)
        if platform in doc:
            if stage == "live":
                doc[platform]["live"] = True
            else:
                key = {"built": "build", "delivering": "upload",
                       "submitted": "review"}.get(stage)
                if key:
                    doc[platform][key] = "complete"
        state_io.save_json(status_json, doc)


def _find_workspace_dir(workspace_id: str) -> str | None:
    if not os.path.isdir(state_io.WORKSPACES_DIR):
        return None
    for name in os.listdir(state_io.WORKSPACES_DIR):
        if name.startswith(workspace_id + "_") or name == workspace_id:
            return os.path.join(state_io.WORKSPACES_DIR, name)
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Update workspace pipeline status")
    parser.add_argument("workspace_id")
    parser.add_argument("stage", choices=STAGES)
    parser.add_argument("--platform", choices=["ios", "android"], default=None)
    args = parser.parse_args()
    update(args.workspace_id, args.stage, args.platform)
    print(f"{args.workspace_id} -> {args.stage}")


if __name__ == "__main__":
    main()
