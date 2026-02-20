"""
filter.py
Filters job postings to keep only US-based, entry-level (0-2 yrs)
SWE / SDE / Backend / Fullstack roles. Excludes senior, staff, intern, etc.
"""

import re
from typing import Optional

# ── Minimum posting date — ignore anything older than this ───────────────────
MIN_POSTED_DATE = "2026-02-01"

# ── Core title patterns — only pure SWE/SDE/backend/fullstack ────────────────
TITLE_INCLUDE = [
    r"\bsoftware engineer\b",
    r"\bsoftware developer\b",
    r"\bswe\b",
    r"\bsde\b",
    r"\bbackend engineer\b",
    r"\bfull.?stack engineer\b",
]

# ── Seniority / role exclusions ──────────────────────────────────────────────
TITLE_EXCLUDE = [
    # Seniority levels
    r"\bsenior\b",
    r"\bsr\.?\b",   # "Sr." / "Sr" abbreviation for Senior
    r"\bstaff\b",
    r"\bprincipal\b",
    r"\blead\b",
    r"\bmanager\b",
    r"\bdirector\b",
    r"\bvp\b",
    r"\bvice president\b",
    r"\barchitect\b",
    r"\biii\b",         # L3+ (senior equiv at many companies)
    r"\biv\b",          # L4+
    r"\b[345]\b",       # L3, L4, L5
    # Non-SWE roles that may contain "engineer"
    r"\bmachine learning engineer\b",
    r"\bml engineer\b",
    r"\bdata engineer\b",
    r"\bdata scientist\b",
    r"\bdevops engineer\b",
    r"\bsite reliability\b",
    r"\bsre\b",
    r"\bsecurity engineer\b",
    r"\bnetwork engineer\b",
    r"\bsolutions engineer\b",
    r"\bsales engineer\b",
    r"\bsupport engineer\b",
    # Employment type exclusions
    r"\bintern(ship)?\b",
    r"\bco.?op\b",
    r"\bpart.?time\b",
    r"\bcontract(or)?\b",
    r"\bfreelance\b",
]

# ── US location signals (allowlist) ──────────────────────────────────────────
US_SIGNALS = [
    "united states", "usa", "us-remote", "us remote",
    "new york", "san francisco", "bay area",
    "seattle", "austin", "los angeles", "boston",
    "chicago", "denver", "atlanta", "washington", "raleigh",
    "houston", "miami", "phoenix", "san jose", "san diego",
    "portland", "minneapolis", "detroit", "pittsburgh",
    "palo alto", "menlo park", "mountain view", "sunnyvale",
    "redwood city", "bellevue", "kirkland", "cambridge",
]

# Country-level blocklist — catches "Remote in Canada", "UK Remote", etc.
COUNTRY_BLOCKLIST = [
    "canada", "uk", "united kingdom", "india", "australia",
    "singapore", "germany", "ireland", "france", "netherlands",
    "europe", "emea", "apac", "latam",
    "romania", "spain", "brazil", "japan", "china", "mexico", "poland",
    "italy", "sweden", "luxembourg", "belgium", "switzerland",
    "israel", "korea", "taiwan", "new zealand", "south africa",
    "denmark", "norway", "finland", "austria", "portugal",
]

# Placeholder strings Greenhouse/ATS systems use when no location is set
PLACEHOLDER_LOCATIONS = {"", "n/a", "na", "location", "tbd", "tbc", "null", "none"}


def _match_any(text: str, patterns: list[str]) -> bool:
    t = text.lower()
    return any(re.search(p, t) for p in patterns)


def is_us_location(location: Optional[str]) -> bool:
    if not location:
        return True  # null/empty = unspecified, treat as remote
    loc = location.strip().lower()
    if loc in PLACEHOLDER_LOCATIONS:
        return True  # placeholder = no real location set, treat as remote
    # Country blocklist first — catches "Remote in Canada", "UK Remote", etc.
    if any(c in loc for c in COUNTRY_BLOCKLIST):
        return False
    # Then allowlist: include if explicit US city/signal found
    if any(sig in loc for sig in US_SIGNALS):
        return True
    # "remote" alone (no country qualifier) counts as US-eligible
    if re.search(r"\bremote\b", loc):
        return True
    return False


def is_relevant_title(title: str) -> bool:
    if not title:
        return False
    # Hard excludes first
    if _match_any(title, TITLE_EXCLUDE):
        return False
    # Must match a core SWE title
    if not _match_any(title, TITLE_INCLUDE):
        return False
    return True


def is_recent_enough(posted_at) -> bool:
    if not posted_at:
        return True  # no date info — include it
    date_str = str(posted_at)[:10]  # take YYYY-MM-DD portion
    try:
        return date_str >= MIN_POSTED_DATE
    except Exception:
        return True


def passes_filter(job: dict) -> bool:
    return (
        is_relevant_title(job.get("title", ""))
        and is_us_location(job.get("location"))
        and is_recent_enough(job.get("posted_at"))
    )
