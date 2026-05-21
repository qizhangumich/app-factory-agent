#!/usr/bin/env bash
# App Factory v2 — start the brain loop (30-min strategic cycle).
# Pass --once to run a single cycle.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"
exec python3 -m brain.brain "$@"
