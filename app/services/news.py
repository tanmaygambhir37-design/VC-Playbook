"""news.py — RSS aggregation, funding-deal extraction, and weekly picks.

Shared by the homepage (Today's VC Brief / Deal Radar) and the VC Pulse page.
Weekly picks live in data/weekly_picks.json — edit that file on GitHub each
week and the site redeploys itself.
"""

import json
import os
import re

import feedparser
import requests
import streamlit as st

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WEEKLY_PICKS_PATH = os.path.join(PROJECT_ROOT, "data", "weekly_picks.json")

FEEDS = {
    "TechCrunch Venture": "https://techcrunch.com/category/venture/feed/",
    "Crunchbase News": "https://news.crunchbase.com/feed",
    "Axios": "https://api.axios.com/feed/",
    "Sifted": "https://sifted.eu/feed",
    "EU-Startups": "https://www.eu-startups.com/feed/",
}

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"

# "Flex raises $70 million", "Prolo secures £4.2M", "Sonata lands €7m seed" ...
_DEAL_RE = re.compile(
    r"^(?P<company>[A-Z][\w.&'-]*(?:\s+[A-Z][\w.&'-]*){0,3})\s+"
    r"(?:raises|raised|secures|lands|closes|nabs|gets|bags|scores)\s+"
    r"(?P<amount>[$€£]\s?\d+(?:[.,]\d+)?\s*(?:million|billion|[MBmbn]{1,2})\b\+?)",
    re.IGNORECASE,
)

_SECTOR_KEYWORDS = {
    "AI": ["ai ", " ai", "artificial intelligence", "llm", "machine learning", "agent"],
    "Fintech": ["fintech", "bank", "payments", "lending", "insurance", "insurtech", "wealth"],
    "Health": ["health", "bio", "medical", "care", "pharma", "therapeutics"],
    "Climate": ["climate", "energy", "solar", "battery", "carbon", "ev "],
    "SaaS": ["saas", "software", "platform", "workflow", "automation"],
    "Defense": ["defense", "defence", "military", "drone"],
    "Space": ["space", "satellite", "orbital"],
    "Crypto": ["crypto", "blockchain", "web3", "stablecoin"],
    "Robotics": ["robot", "robotics", "autonomous"],
}


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_feed(source: str, url: str) -> list[dict]:
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
        parsed = feedparser.parse(response.content)
        return [
            {
                "source": source,
                "title": entry.get("title", "Untitled"),
                "link": entry.get("link", "#"),
                "published": entry.get("published", entry.get("updated", "")),
            }
            for entry in parsed.entries[:10]
        ]
    except Exception:
        return []


def fetch_all_feeds() -> tuple[list[list[dict]], list[str]]:
    """Returns (list of per-source item lists, list of unavailable source names)."""
    groups, dead = [], []
    for source, url in FEEDS.items():
        items = fetch_feed(source, url)
        (groups if items else dead).append(items if items else source)
    return [g for g in groups if isinstance(g, list)], [d for d in dead if isinstance(d, str)]


def interleave(groups: list[list[dict]]) -> list[dict]:
    """Mix sources so the top of the wall isn't a single outlet."""
    if not groups:
        return []
    if len(groups) == 1:
        return groups[0]
    mixed = [item for bundle in zip(*groups) for item in bundle]
    seen = {id(i) for i in mixed}
    mixed += [i for g in groups for i in g if id(i) not in seen]
    return mixed


def guess_sector(title: str) -> str:
    lowered = f" {title.lower()} "
    for sector, keywords in _SECTOR_KEYWORDS.items():
        if any(k in lowered for k in keywords):
            return sector
    return "Venture"


# Headlines often lead with descriptors: "Crypto VC firm Paradigm raises...",
# "London-based Prolo secures..." — strip them so only the name remains.
_DESCRIPTOR_WORDS = {"crypto", "vc", "firm", "startup", "company", "platform", "fintech", "app", "maker"}


def _clean_company(name: str) -> str:
    tokens = name.split()
    while len(tokens) > 1 and (tokens[0].lower() in _DESCRIPTOR_WORDS or tokens[0].lower().endswith("-based")):
        tokens.pop(0)
    return " ".join(tokens)


def extract_deals(items: list[dict]) -> list[dict]:
    """Pull structured funding rounds out of headline text."""
    deals = []
    for item in items:
        match = _DEAL_RE.match(item["title"].strip())
        if not match:
            continue
        deals.append(
            {
                **item,
                "company": _clean_company(match.group("company")),
                "amount": re.sub(r"\s+", "", match.group("amount")).replace("million", "M").replace("billion", "B"),
                "sector": guess_sector(item["title"]),
            }
        )
    return deals


def load_weekly_picks() -> dict:
    try:
        with open(WEEKLY_PICKS_PATH) as fh:
            return json.load(fh)
    except Exception:
        return {"week_of": "", "deals": [], "videos": [], "articles": []}
