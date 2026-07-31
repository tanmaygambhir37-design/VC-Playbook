"""VC Pulse — full news wall, deal radar, and weekly picks."""

import html
import os
import sys

import streamlit as st

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(APP_DIR)
sys.path.append(APP_DIR)
sys.path.append(PROJECT_ROOT)
from components.footer import email_capture, footer
from components.navigation import sidebar
from components.theme import apply_theme, page_header, section_title
from services.analytics import track_event, track_page
from services.news import extract_deals, fetch_all_feeds, interleave, load_weekly_picks
from state import set_prefill_deal

st.set_page_config(page_title="VC Pulse | VC Playbook", page_icon="📗", layout="wide")
apply_theme()
sidebar()
track_page("vc-pulse", "VC Pulse")

page_header("VC Pulse", "The latest venture capital news, deals, and analysis — refreshed automatically.", "News")


def news_card(item: dict) -> str:
    published = item["published"][:22] if item.get("published") else ""
    return f"""
        <a class="vcl-news-card" href="{html.escape(item['link'])}" target="_blank">
            <div class="vcl-news-source">{html.escape(item['source'])}</div>
            <div class="vcl-news-title">{html.escape(item['title'])}</div>
            <div class="vcl-news-meta">{html.escape(published)}</div>
        </a>
    """


def deal_card(deal: dict) -> str:
    return f"""
        <a class="vcl-deal-card" style="display:block; text-decoration:none;" href="{html.escape(deal['link'])}" target="_blank">
            <div class="vcl-deal-name">{html.escape(deal['company'])}
                <span class="vcl-deal-sector">{html.escape(deal['sector'])}</span></div>
            <div class="vcl-deal-amount">{html.escape(deal['amount'])}</div>
            <div class="vcl-deal-body">{html.escape(deal['title'])}</div>
        </a>
    """


def weekly_deal_card(deal: dict) -> str:
    lead = f"<strong>Lead:</strong> {html.escape(deal['lead'])}<br>" if deal.get("lead") else ""
    investors = f"<strong>Investors:</strong> {html.escape(deal['investors'])}<br>" if deal.get("investors") else ""
    return f"""
        <div class="vcl-deal-card">
            <div class="vcl-news-source">{html.escape(deal.get('category', 'Venture'))}</div>
            <div class="vcl-deal-name">{html.escape(deal['company'])}
                <span class="vcl-deal-sector">{html.escape(deal.get('sector', ''))}</span></div>
            <div class="vcl-deal-amount">{html.escape(deal.get('amount', ''))} <span style="font-size:0.8rem; color:#4B5164; font-weight:600;">{html.escape(deal.get('round', ''))}</span></div>
            <div class="vcl-deal-body">{lead}{investors}{html.escape(deal.get('note', ''))}</div>
        </div>
    """


def grid(cards: list[str], per_row: int = 3) -> None:
    for row_start in range(0, len(cards), per_row):
        cols = st.columns(per_row)
        for col, card in zip(cols, cards[row_start:row_start + per_row]):
            with col:
                st.markdown(card, unsafe_allow_html=True)


with st.spinner("Pulling the latest VC headlines..."):
    groups, dead_sources = fetch_all_feeds()

all_items = [item for group in groups for item in group]
deals = extract_deals(all_items)

def analyze_row(items: list[dict], per_row: int, key_prefix: str, render) -> None:
    """Render cards with an Analyze button under each — every deal on this
    page is one click from a filled scorecard, not just the first one."""
    for row_start in range(0, len(items), per_row):
        cols = st.columns(per_row)
        for offset, (col, deal) in enumerate(zip(cols, items[row_start:row_start + per_row])):
            with col:
                st.markdown(render(deal), unsafe_allow_html=True)
                if st.button(
                    f"Analyze {deal['company']} →",
                    key=f"{key_prefix}_{row_start + offset}",
                    use_container_width=True,
                ):
                    set_prefill_deal(deal)
                    track_event("analyze_deal_clicked", company=deal.get("company"),
                                sector=deal.get("sector"), placement=key_prefix)
                    st.switch_page("pages/1_Startup_Screening.py")


if deals:
    section_title("Deal Radar", "Funding rounds detected in today's news — analyze any of them in the simulator.")
    analyze_row(deals[:9], 3, "radar", deal_card)

picks = load_weekly_picks()
if picks.get("deals"):
    section_title(
        "This Week's Picks",
        f"Hand-picked deals worth studying · Week of {picks.get('week_of', '')} · {picks.get('as_of_label', '')}",
    )
    analyze_row(picks["deals"], 2, "weekly", weekly_deal_card)

section_title("All Headlines", "Everything from the wire, by source.")
if not groups:
    st.warning("No feeds could be reached right now — try refreshing in a minute.")
else:
    sources = [g[0]["source"] for g in groups]
    tabs = st.tabs(["All"] + sources)
    with tabs[0]:
        grid([news_card(i) for i in interleave(groups)[:18]])
    for tab, group in zip(tabs[1:], groups):
        with tab:
            grid([news_card(i) for i in group])

if dead_sources:
    st.caption(f"Currently unavailable: {', '.join(dead_sources)}")

section_title("Spotlight of the Week", "One video and one read, refreshed weekly.")
s1, s2 = st.columns(2)
with s1:
    st.markdown('<div class="vcl-card-kicker">Video of the Week</div>', unsafe_allow_html=True)
    for video in picks.get("videos", []):
        st.markdown(f"**[{video['title']}]({video['url']})**  \n{video.get('why', '')}")
    if not picks.get("videos"):
        st.caption("Coming this week.")
with s2:
    st.markdown('<div class="vcl-card-kicker">Article of the Week</div>', unsafe_allow_html=True)
    for article in picks.get("articles", []):
        st.markdown(f"**[{article['title']}]({article['url']})**  \n{article.get('why', '')}")
    if not picks.get("articles"):
        st.caption("Coming this week.")

email_capture()
footer()
