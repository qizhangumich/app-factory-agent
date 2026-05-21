#!/usr/bin/env bash
# App Factory v2 — deploy every workspace currently sitting in queue/built.
# Usage: ./deploy_all.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT}"

BUILT_IDS="$(python3 -c "import json; print(' '.join(e['workspace_id'] for e in json.load(open('state/queue.json')).get('built', [])))")"

if [[ -z "${BUILT_IDS}" ]]; then
  echo "queue/built is empty — nothing to deploy"
  exit 0
fi

for WS_ID in ${BUILT_IDS}; do
  WS_PATH="$(find workspaces -maxdepth 1 -type d -name "${WS_ID}_*" | head -n1)"
  if [[ -n "${WS_PATH}" ]]; then
    echo "### ${WS_ID}"
    ./delivery/scripts/deploy_workspace.sh "${WS_PATH}"
  fi
done
