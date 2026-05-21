#!/usr/bin/env bash
# App Factory v2 — pull sales data from the stores and fold it into state.
#
# Fetches App Store Connect + Google Play sales reports, then calls the brain's
# revenue tracker per app. Requires fastlane + the per-account credentials.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

echo "Pulling revenue reports..."
echo
echo "  iOS:     fastlane spaceship / App Store Connect sales reports"
echo "  Android: Google Play earnings reports (gsutil from the reporting bucket)"
echo
echo "For each (workspace_id, account_id, amount, day) record, run:"
echo "  python3 -c \"from brain import revenue_tracker as r;"
echo "             r.record_revenue('ws_001','ios_001',0.84,'2026-05-22')\""
echo
echo "Then refresh system rollups:"
python3 -c "from brain import revenue_tracker as r; print(r.refresh())"
