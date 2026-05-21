"""Shared state I/O for the brain, factory, and delivery layers.

All persistent state lives in ``state/*.json`` as plain JSON so the system is
crash-safe and restartable. Writes are atomic (write-temp-then-rename) so a
crash mid-write never corrupts a state file.
"""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone

# Repo root = parent of the brain/ directory.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATE_DIR = os.path.join(ROOT, "state")
QUEUE_DIR = os.path.join(ROOT, "queue")
WORKSPACES_DIR = os.path.join(ROOT, "workspaces")
CONFIG_DIR = os.path.join(ROOT, "config")
DATA_DIR = os.path.join(ROOT, "data")

STATE_FILES = {
    "state": os.path.join(STATE_DIR, "state.json"),
    "queue": os.path.join(STATE_DIR, "queue.json"),
    "accounts": os.path.join(STATE_DIR, "accounts.json"),
    "apps": os.path.join(STATE_DIR, "apps.json"),
    "revenue": os.path.join(STATE_DIR, "revenue.json"),
    "build_log": os.path.join(STATE_DIR, "build_log.json"),
    "decisions": os.path.join(STATE_DIR, "decisions.json"),
}


def now_iso() -> str:
    """UTC timestamp in ISO-8601 with a trailing Z."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def save_json(path: str, data: dict) -> None:
    """Atomically write ``data`` as pretty JSON to ``path``."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def load_state(name: str) -> dict:
    """Load a named state file, e.g. ``load_state("accounts")``."""
    return load_json(STATE_FILES[name])


def save_state(name: str, data: dict) -> None:
    """Save a named state file, stamping ``updated_at``."""
    if isinstance(data, dict):
        data["updated_at"] = now_iso()
    save_json(STATE_FILES[name], data)
