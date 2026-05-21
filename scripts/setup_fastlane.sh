#!/usr/bin/env bash
# App Factory v2 — Fastlane + code-signing setup. [HUMAN GATE]
# Run once on macOS after credentials are in config/fastlane_env/.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}/delivery"

echo "Installing fastlane via bundler..."
bundle install

echo
echo "Initialising code signing with match."
echo "match stores certs + profiles in a private git repo (MATCH_GIT_URL)."
echo "For each iOS account, source its env file and run:"
echo
echo "    source config/fastlane_env/ios_001.env"
echo "    bundle exec fastlane match appstore --readonly false"
echo
echo "That generates/uploads App Store signing certificates once. CI and the"
echo "delivery scripts then sync them read-only. Repeat per iOS account."
