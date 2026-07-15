"""VC Pulse — live venture capital news wall + curated learning resources.

News comes from public RSS feeds (no scraping, no accounts). Curated
YouTube / Substack sections are plain lists below — edit them to add links.
"""

import html
import os
import sys

import feedparser
import requests
import streamlit as st

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(APP_DIR)
sys.path.append(APP_DIR)
sys.path.append(PROJECT_ROOT)
from components.footer import footer
from components.navigation import sidebar
from components.theme import apply_theme, page_header, section_title

st.set_page_config(page_title="VC Pulse | VC Playbook", page_icon="📗", layout="wide")
apply_theme()
sidebar()

page_header("VC Pulse", "The latest venture capital news, deals, and analysis — refreshed automatically.", "News")

FEEDS = {
    "TechCrunch Venture": "https://techcrunch.com/category/venture/feed/",
    "Crunchbase News": "https://news.crunchbase.com/feed",
    "Axios": "https://api.axios.com/feed/",
    "Sifted": "https://sifted.eu/feed",
    "EU-Startups": "https://www.eu-startups.com/feed/",
}

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"

# Add your favorite resources here: ("Title", "https://link", "one-line why")
CURATED_YOUTUBE: list[tuple[str, str, str]] = []
CURATED_SUBSTACK: list[tuple[str, str, str]] = []


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
            for entry in parsed.entries[:8]
        ]
    except Exception:
        return []


def news_card(item: dict) -> str:
    published = item["published"][:22] if item["published"] else ""
    return f"""
        <a class="vcl-news-card" href="{html.escape(item['link'])}" target="_blank">
            <div class="vcl-news-source">{html.escape(item['source'])}</div>
            <div class="vcl-news-title">{html.escape(item['title'])}</div>
            <div class="vcl-news-meta">{html.escape(published)}</div>
        </a>
    """


with st.spinner("Pulling the latest VC headlines..."):
    all_items = []
    dead_sources = []
    for source, url in FEEDS.items():
        items = fetch_feed(source, url)
        if items:
            all_items.append(items)
        else:
            dead_sources.append(source)

if not all_items:
    st.warning("No feeds could be reached right now — try refreshing in a minute.")
else:
    sources = [items[0]["source"] for items in all_items]
    tabs = st.tabs(["All"] + sources)

    with tabs[0]:
        # Interleave sources so the top of the wall is mixed, not one outlet
        mixed = [item for group in zip(*[iter(i) for i in all_items]) for item in group] if len(all_items) > 1 else all_items[0]
        mixed = mixed or [item for items in all_items for item in items]
        for row_start in range(0, min(len(mixed), 18), 3):
            cols = st.columns(3)
            for col, item in zip(cols, mixed[row_start:row_start + 3]):
                with col:
                    st.markdown(news_card(item), unsafe_allow_html=True)

    for tab, items in zip(tabs[1:], all_items):
        with tab:
            for row_start in range(0, len(items), 3):
                cols = st.columns(3)
                for col, item in zip(cols, items[row_start:row_start + 3]):
                    with col:
                        st.markdown(news_card(item), unsafe_allow_html=True)

if dead_sources:
    st.caption(f"Currently unavailable: {', '.join(dead_sources)}")

section_title("Watch & Read", "Hand-picked videos and articles for learning venture capital.")
y1, y2 = st.columns(2)
with y1:
    st.markdown('<div class="vcl-card-kicker">YouTube</div>', unsafe_allow_html=True)
    if CURATED_YOUTUBE:
        for title, link, why in CURATED_YOUTUBE:
            st.markdown(f"- [{title}]({link}) — {why}")
    else:
        st.caption("Curated videos coming soon.")
with y2:
    st.markdown('<div class="vcl-card-kicker">Substack & Articles</div>', unsafe_allow_html=True)
    if CURATED_SUBSTACK:
        for title, link, why in CURATED_SUBSTACK:
            st.markdown(f"- [{title}]({link}) — {why}")
    else:
        st.caption("Curated articles coming soon.")

footer()
