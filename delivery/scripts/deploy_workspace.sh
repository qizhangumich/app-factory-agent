#!/usr/bin/env bash
# App Factory v2 — deploy one workspace to the stores.
#
# Reads the workspace manifest to learn which accounts own the app, loads
# that account's Fastlane credentials, then builds + uploads each platform.
# Runs on macOS (Xcode required for iOS).
#
# Usage: ./deploy_workspace.sh workspaces/ws_001_tipcalcdeluxe
set -euo pipefail

WS_PATH="${1:?usage: deploy_workspace.sh <workspace_path>}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WS_JSON="${WS_PATH}/workspace.json"

if [[ ! -f "${WS_JSON}" ]]; then
  echo "error: ${WS_JSON} not found" >&2
  exit 1
fi

jq_get() { python3 -c "import json,sys; v=json.load(open('${WS_JSON}')).get('$1'); print('' if v is None else v)"; }

# Load an account's credentials. Locally this sources config/fastlane_env/<id>.env;
# on a CI runner that file is absent and the credentials already live in the
# environment (injected from GitHub Secrets), so a missing file is not an error.
load_env() {
  local env_file="${ROOT}/config/fastlane_env/$1.env"
  if [[ -f "${env_file}" ]]; then
    echo "    sourcing ${env_file}"
    # shellcheck disable=SC1090
    source "${env_file}"
  else
    echo "    no .env for $1 — using credentials from the environment (CI mode)"
  fi
}

WS_ID="$(jq_get workspace_id)"
IOS_ACCOUNT="$(jq_get ios_account)"
ANDROID_ACCOUNT="$(jq_get android_account)"
BUNDLE_IOS="$(jq_get bundle_id_ios)"
BUNDLE_ANDROID="$(jq_get bundle_id_android)"
PLATFORMS="$(python3 -c "import json; print(' '.join(json.load(open('${WS_JSON}'))['platforms']))")"

echo "==> Deploying ${WS_ID} (${PLATFORMS})"

# --- iOS -------------------------------------------------------------------
if [[ "${PLATFORMS}" == *ios* && -n "${IOS_ACCOUNT}" ]]; then
  echo "--> iOS via account ${IOS_ACCOUNT}"
  load_env "${IOS_ACCOUNT}"
  SCHEME="$(ls "${WS_PATH}/ios" | grep -E '\.xcodeproj$' | head -n1 | sed 's/\.xcodeproj//')"
  ( cd "${ROOT}/delivery" && bundle exec fastlane ios deploy \
      app_dir:"${ROOT}/${WS_PATH}/ios" \
      scheme:"${SCHEME}" \
      bundle_id:"${BUNDLE_IOS}" )
  python3 -m brain.update_workspace_status "${WS_ID}" delivering --platform ios
fi

# --- Android ---------------------------------------------------------------
if [[ "${PLATFORMS}" == *android* && -n "${ANDROID_ACCOUNT}" ]]; then
  echo "--> Android via account ${ANDROID_ACCOUNT}"
  load_env "${ANDROID_ACCOUNT}"
  ( cd "${ROOT}/delivery" && bundle exec fastlane android deploy \
      app_dir:"${ROOT}/${WS_PATH}/android" \
      bundle_id:"${BUNDLE_ANDROID}" )
  python3 -m brain.update_workspace_status "${WS_ID}" delivering --platform android
fi

python3 -m brain.update_workspace_status "${WS_ID}" submitted
echo "==> ${WS_ID} uploaded. [HUMAN GATE] review metadata and submit for review."
