"""Platform router — decides iOS-first, Android-first, or dual publish.

Higher-ARPU categories ship iOS first; volume categories dual-publish.
Hardware-sensor apps that rely on iOS-only APIs stay iOS-only.
"""
from __future__ import annotations

# Categories whose flagship apps depend on iOS-only sensor/media APIs.
IOS_ONLY_HINTS = {"coremotion", "avaudioengine", "photokit"}


def route_platform(idea: dict) -> dict:
    """Return a routing decision for an app idea.

    Keys: primary ('ios' | 'android' | 'both'), secondary, delay_secondary (days).
    """
    category = idea.get("category", "")

    # An explicit platforms list on the spec always wins.
    platforms = idea.get("platforms")
    if platforms:
        if set(platforms) == {"ios", "android"}:
            return {"primary": "both", "secondary": None, "delay_secondary": 0}
        if platforms == ["ios"]:
            return {"primary": "ios", "secondary": None, "delay_secondary": 0}
        if platforms == ["android"]:
            return {"primary": "android", "secondary": None, "delay_secondary": 0}

    if category in ("Utilities", "Productivity", "Health & Fitness", "Health"):
        return {"primary": "ios", "secondary": "android", "delay_secondary": 7}
    if category in ("Games", "Entertainment", "Education", "Reference", "Custom"):
        return {"primary": "both", "secondary": None, "delay_secondary": 0}
    return {"primary": "ios", "secondary": "android", "delay_secondary": 14}
