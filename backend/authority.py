"""
ZeroHour - Authority verification.

Uses googlesearch-python to query official sources and
BeautifulSoup to validate the match.
"""

import re
import time
import requests
from bs4 import BeautifulSoup  # type: ignore

# Domains considered authoritative
AUTHORITY_DOMAINS = [
    "police.gov", "fbi.gov", "cdc.gov", "fema.gov", "ready.gov",
    "who.int", "un.org", "reuters.com", "apnews.com", "bbc.com",
    "ndtv.com", "thehindu.com", "pib.gov.in",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}


def _is_authority_url(url: str) -> bool:
    return any(domain in url for domain in AUTHORITY_DOMAINS)


def _fetch_snippet(url: str, keyword: str, timeout: int = 5) -> bool:
    """Return True if keyword appears on the fetched page."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text(separator=" ").lower()
        return keyword.lower() in text
    except Exception:
        return False


def verify_authority(keywords: list[str], location: str = "") -> dict:
    """
    Search for authority confirmation for a set of crisis keywords.

    Returns:
        {
          "confirmed": bool,
          "source_url": str | None,
          "domain": str | None,
          "latency_ms": float,
        }
    """
    try:
        from googlesearch import search  # type: ignore
    except ImportError:
        return {"confirmed": False, "source_url": None, "domain": None, "latency_ms": 0}

    query_parts = " ".join(keywords[:3])
    if location:
        query_parts += f" {location}"
    query = f"{query_parts} site:police.gov OR site:reuters.com OR site:apnews.com OR site:bbc.com"

    t0 = time.time()
    try:
        results = list(search(query, num_results=5, sleep_interval=1))
    except Exception as exc:
        print(f"[Authority] Google search failed — {exc}")
        return {"confirmed": False, "source_url": None, "domain": None, "latency_ms": 0}

    for url in results:
        if _is_authority_url(url):
            confirmed = _fetch_snippet(url, keywords[0] if keywords else "")
            latency = round((time.time() - t0) * 1000, 1)
            domain = re.search(r"https?://([^/]+)", url)
            return {
                "confirmed": confirmed,
                "source_url": url,
                "domain": domain.group(1) if domain else url,
                "latency_ms": latency,
            }

    return {
        "confirmed": False,
        "source_url": None,
        "domain": None,
        "latency_ms": round((time.time() - t0) * 1000, 1),
    }
