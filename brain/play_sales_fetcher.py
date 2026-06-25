"""Google Play sales fetcher — Layer 1 input (stub).

Google Play's sales data isn't in the Publishing API we already use for
delivery. It lives in two places:

  1. Reporting API  (downloads, installs, crashes — free)
     https://developers.google.com/play/developer/reporting
     Needs OAuth scope:
        https://www.googleapis.com/auth/playdeveloperreporting

  2. Financial Reports  (revenue from paid apps + IAP)
     A monthly CSV dropped into a Google Cloud Storage bucket
     owned by the developer. You list/download with the standard
     google-cloud-storage SDK.

Phase 1 ships only FREE apps with NO IAP, so the financial reports
are all zero — there's nothing useful to fetch yet. When the brain
starts shipping paid apps (Phase 3+) we'll wire this up.

For now this module returns an empty list and prints a guidance
message. The orchestrator in scripts/refresh_revenue.py just sees
"0 Play events" and moves on.
"""

from __future__ import annotations


def fetch_sales(report_date: str | None = None) -> list[dict]:
    """Stub: returns []. See module docstring for the real wiring."""
    return []


def map_to_workspace(events: list[dict]) -> list[dict]:
    return events


if __name__ == "__main__":
    print("Google Play sales fetcher: not yet wired.")
    print("Reason: Phase 1 apps are free with no IAP, so financial reports = $0.")
    print("Setup needed when first paid app ships:")
    print("  1. Enable the Play Developer Reporting API in Cloud Console")
    print("  2. Re-auth OAuth with scope:")
    print("       https://www.googleapis.com/auth/playdeveloperreporting")
    print("  3. For revenue: install google-cloud-storage and pull from")
    print("       gs://pubsite_prod_<DEVELOPER_ID>/sales/")
