"""news.py — RSS aggregation, funding-deal extraction, and weekly picks.

Shared by the homepage (Today's VC Brief / Deal Radar) and the VC Pulse page.
Weekly picks live in data/weekly_picks.json — edit that file on GitHub each
week and the site redeploys itself.
"""

import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime

import feedparser
import requests
import streamlit as st

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WEEKLY_PICKS_PATH = os.path.join(PROJECT_ROOT, "data", "weekly_picks.json")
PREDICTIONS_PATH = os.path.join(PROJECT_ROOT, "data", "predictions.json")

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


def fetch_feed(source: str, url: str) -> list[dict]:
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=6)
        parsed = feedparser.parse(response.content)
        items = [
            {
                "source": source,
                "title": entry.get("title", "Untitled"),
                "link": entry.get("link", "#"),
                "published": entry.get("published", entry.get("updated", "")),
            }
            for entry in parsed.entries[:25]
        ]
        # Axios is a general-news feed — keep only VC/business headlines
        if source == "Axios":
            items = [i for i in items if is_vc_relevant(i["title"])]
        return items[:10]
    except Exception:
        return []


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_all_feeds() -> tuple[list[list[dict]], list[str]]:
    """Returns (list of per-source item lists, list of unavailable source names).
    Feeds are fetched in parallel so a slow source doesn't block the page."""
    with ThreadPoolExecutor(max_workers=len(FEEDS)) as pool:
        results = list(pool.map(lambda kv: (kv[0], fetch_feed(*kv)), FEEDS.items()))
    groups = [items for _, items in results if items]
    dead = [source for source, items in results if not items]
    return groups, dead


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
# "London-based Prolo secures...", "EQT-backed Syntetica lands...",
# "Robotics startup Monumental raises..." — strip them so only the name remains.
_DESCRIPTOR_WORDS = {"crypto", "vc", "firm", "startup", "company", "platform", "fintech", "app", "maker"}
# Words that describe a company category — the real name usually follows them.
_DESCRIPTOR_ANYWHERE = {"startup", "platform", "firm", "company", "maker", "app", "provider", "developer"}


def _clean_company(name: str) -> str:
    tokens = name.split()
    # If a category word appears with a name after it, keep only the tail:
    # "German DeepTech startup kausable" -> "kausable", "Crypto VC firm Paradigm" -> "Paradigm"
    idxs = [i for i, t in enumerate(tokens) if t.lower().strip(",.") in _DESCRIPTOR_ANYWHERE]
    if idxs and idxs[-1] < len(tokens) - 1:
        tokens = tokens[idxs[-1] + 1:]
    else:
        while len(tokens) > 1 and (
            tokens[0].lower() in _DESCRIPTOR_WORDS
            or tokens[0].lower().endswith(("-based", "-backed"))
        ):
            tokens.pop(0)
    return " ".join(tokens)


def _looks_like_name(name: str) -> bool:
    """Reject extractions that are still generic descriptions, not a company name."""
    words = name.split()
    return bool(words) and len(words) <= 4 and not any(
        w.lower().strip(",.") in _DESCRIPTOR_ANYWHERE for w in words
    )


# Keywords that make a headline VC/business-relevant. Used to keep general-news
# feeds (Axios) from putting geopolitics in a "VC Brief".
_RELEVANT_RE = re.compile(
    r"(?i)(\brais(e|es|ed|ing)\b|\bfunding\b|\bventure\b|\bseed\b|\bseries [a-e]\b|"
    r"\bipo\b|\bacqui(re|red|sition)\b|\bvaluation\b|\binvest(s|ed|ment|or)?\b|"
    r"\bfunding round\b|\bunicorn\b|\bvc\b|\bstartup\b|\bmerger\b|\bspac\b)",
)


def is_vc_relevant(title: str) -> bool:
    return bool(_RELEVANT_RE.search(title))


def extract_deals(items: list[dict]) -> list[dict]:
    """Pull structured funding rounds out of headline text."""
    deals = []
    for item in items:
        match = _DEAL_RE.match(item["title"].strip())
        if not match:
            continue
        company = _clean_company(match.group("company"))
        if not _looks_like_name(company):
            continue  # skip headlines that don't cleanly name the company
        deals.append(
            {
                **item,
                "company": company,
                "amount": re.sub(r"\s+", "", match.group("amount")).replace("million", "M").replace("billion", "B"),
                "sector": guess_sector(item["title"]),
            }
        )
    return deals


def load_weekly_picks() -> dict:
    """Weekly picks, with a staleness guard: if week_of (ISO date) is more
    than 14 days old, the curated sections hide so the site never looks
    abandoned. `stale` is set on the returned dict."""
    empty = {"week_of": "", "deals": [], "videos": [], "articles": [], "stale": True}
    try:
        with open(WEEKLY_PICKS_PATH) as fh:
            picks = json.load(fh)
    except Exception:
        return empty
    try:
        week = datetime.strptime(picks.get("week_of", ""), "%Y-%m-%d").date()
        picks["stale"] = (date.today() - week).days > 14
    except ValueError:
        picks["stale"] = False  # unparseable date -> show rather than hide
    # Auto-title videos: paste just a URL in the JSON and the real YouTube
    # title is fetched here.
    for video in picks.get("videos", []):
        if not video.get("title") or video["title"] == "Video of the Week":
            video["title"] = youtube_title(video.get("url", "")) or "Video of the Week"
    return picks


@st.cache_data(ttl=86400, show_spinner=False)
def youtube_title(url: str) -> str | None:
    """Video title via YouTube's public oEmbed endpoint — no API key needed."""
    try:
        response = requests.get(
            "https://www.youtube.com/oembed",
            params={"url": url, "format": "json"},
            headers={"User-Agent": USER_AGENT},
            timeout=6,
        )
        return response.json().get("title")
    except Exception:
        return None


SUBSTACK_FEED = "https://tanmaydiary.substack.com/feed"


@st.cache_data(ttl=3600, show_spinner=False)
def latest_substack_post() -> dict | None:
    """Newest post from the author's Substack, or None if unreachable."""
    try:
        response = requests.get(SUBSTACK_FEED, headers={"User-Agent": USER_AGENT}, timeout=6)
        parsed = feedparser.parse(response.content)
        entry = parsed.entries[0]
        return {"title": entry.get("title", ""), "link": entry.get("link", "#")}
    except Exception:
        return None


def load_predictions() -> list[dict]:
    """Public track record, newest call first."""
    try:
        with open(PREDICTIONS_PATH) as fh:
            preds = json.load(fh).get("predictions", [])
    except Exception:
        return []
    return sorted(preds, key=lambda p: p.get("date", ""), reverse=True)


def prediction_scorecard(preds: list[dict]) -> dict:
    """Hit rate over resolved calls; partial counts as half."""
    resolved = [p for p in preds if p.get("status") in {"correct", "wrong", "partial"}]
    score = sum({"correct": 1.0, "partial": 0.5}.get(p["status"], 0.0) for p in resolved)
    hit_rate = round(100 * score / len(resolved)) if resolved else None
    return {
        "total": len(preds),
        "open": sum(1 for p in preds if p.get("status") == "open"),
        "resolved": len(resolved),
        "hit_rate": hit_rate,
    }
