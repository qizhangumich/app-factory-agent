#!/usr/bin/env bash
# App Factory v2 — one-time environment setup.
# The brain and factory use only the Python standard library, so there is
# nothing to pip-install. This script verifies the toolchain and reports.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

echo "App Factory v2 — environment check"
echo "=================================="

command -v python3 >/dev/null 2>&1 && echo "  python3 : $(python3 --version)" \
  || echo "  python3 : MISSING (required for brain + factory)"
command -v ruby    >/dev/null 2>&1 && echo "  ruby    : $(ruby --version)" \
  || echo "  ruby    : MISSING (required for delivery / fastlane)"
command -v bundle  >/dev/null 2>&1 && echo "  bundler : $(bundle --version)" \
  || echo "  bundler : MISSING (run 'gem install bundler')"
command -v xcodebuild >/dev/null 2>&1 && echo "  xcode   : $(xcodebuild -version | head -1)" \
  || echo "  xcode   : MISSING (required for iOS builds — macOS only)"
command -v gradle  >/dev/null 2>&1 && echo "  gradle  : $(gradle --version | grep Gradle)" \
  || echo "  gradle  : not on PATH (Android Studio bundles its own)"

echo
echo "State files:"
for f in state/*.json; do echo "  $f"; done

echo
echo "Next steps:"
echo "  1. Install fastlane:  (cd delivery && bundle install)"
echo "  2. Fill credentials:  config/fastlane_env/  (see its README.md)"
echo "  3. Run signing setup: scripts/setup_fastlane.sh"
echo "  4. Start the brain:   scripts/run_brain.sh"
