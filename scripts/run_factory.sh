#!/usr/bin/env bash
# App Factory v2 — claim the next spec for the factory.
#
# The factory's code generation is performed by a Claude Code worker session,
# not by this script. This script scaffolds the next workspace and tells the
# operator (or an automation wrapper) to run a worker against it.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

WS_PATH="$(python3 -m factory.factory claim)"
if [[ -z "${WS_PATH}" || "${WS_PATH}" == *"empty"* ]]; then
  echo "Nothing to build — queue/pending is empty."
  exit 0
fi

echo
echo "Workspace scaffolded: ${WS_PATH}"
echo "Now run a Claude Code factory worker inside it to generate ios/ + android/ code."
echo "When the worker finishes:  python3 -m factory.factory complete <workspace_id>"
