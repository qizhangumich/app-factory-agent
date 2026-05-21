#!/usr/bin/env bash
# App Factory v2 — run the delivery pipeline for every built workspace.
# Builds, signs, and uploads each app sitting in queue/built. macOS only
# (Xcode required for iOS). The human gate performs the final store submit.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"
exec ./delivery/scripts/deploy_all.sh
