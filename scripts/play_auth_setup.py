#!/usr/bin/env python3
"""
App Factory v2 - Google Play OAuth2 Setup
==========================================
One-time authorization using your own Google account.
Saves credentials to config/play_oauth_token.json for use by play_deliver.py.

Steps:
  1. Go to Google Cloud Console -> APIs & Services -> Credentials
  2. Click "Create Credentials" -> "OAuth 2.0 Client ID"
  3. Application type: "Desktop app" -> name it "appfactory-local" -> Create
  4. Download the JSON -> save to config/play_oauth_client.json
  5. Run this script: python scripts/play_auth_setup.py
  6. A browser opens -> log in with jeremy4crypto@gmail.com -> Allow
  7. Token saved to config/play_oauth_token.json -> delivery script ready
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
CLIENT_FILE = REPO_ROOT / "config" / "play_oauth_client.json"
TOKEN_FILE  = REPO_ROOT / "config" / "play_oauth_token.json"

SCOPES = ["https://www.googleapis.com/auth/androidpublisher"]

def main():
    if not CLIENT_FILE.exists():
        print(f"\n[ERROR] OAuth client file not found: {CLIENT_FILE}")
        print("\nTo create it:")
        print("  1. Go to https://console.cloud.google.com/apis/credentials")
        print("     (make sure project 'appfactory-play' is selected)")
        print("  2. Click 'Create Credentials' -> 'OAuth 2.0 Client ID'")
        print("  3. Application type: 'Desktop app'")
        print("  4. Name: 'appfactory-local' -> Create")
        print("  5. Click the download icon (JSON) -> save to:")
        print(f"       {CLIENT_FILE}")
        print("  6. Re-run this script")
        sys.exit(1)

    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.oauth2.credentials import Credentials
    import json

    print("\nStarting OAuth2 authorization flow...")
    print("A browser window will open. Log in with jeremy4crypto@gmail.com and click Allow.\n")

    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_FILE), SCOPES)
    creds = flow.run_local_server(port=0)

    # Save token
    token_data = {
        "token":         creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri":     creds.token_uri,
        "client_id":     creds.client_id,
        "client_secret": creds.client_secret,
        "scopes":        list(creds.scopes),
    }
    TOKEN_FILE.write_text(json.dumps(token_data, indent=2))
    print(f"\n[OK] Token saved to: {TOKEN_FILE}")
    print("\nYou can now run: python scripts/play_deliver.py")

if __name__ == "__main__":
    main()
