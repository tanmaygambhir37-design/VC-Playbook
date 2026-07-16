import html
import os
import sys

import streamlit as st

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(APP_DIR)
sys.path.append(APP_DIR)
sys.path.append(PROJECT_ROOT)
from components.footer import footer
from components.theme import (
    GITHUB_URL,
    LINKEDIN_URL,
    SUBSTACK_URL,
    apply_theme,
    hide_sidebar,
    landing_header,
    section_title,
)
from services.news import extract_deals, fetch_all_feeds, interleave, latest_substack_post, load_weekly_picks

st.set_page_config(page_title="VC Playbook", page_icon="📗", layout="wide", initial_sidebar_state="collapsed")
apply_theme()
hide_sidebar()


def news_line(item: dict) -> str:
    return f"""
        <a class="vcl-news-card" href="{html.escape(item['link'])}" target="_blank">
            <div class="vcl-news-source">{html.escape(item['source'])}</div>
            <div class="vcl-news-title">{html.escape(item['title'])}</div>
        </a>
    """


def deal_card_html(deal: dict) -> str:
    return f"""
        <a class="vcl-deal-card" style="display:block; text-decoration:none;" href="{html.escape(deal['link'])}" target="_blank">
            <div class="vcl-news-source">{html.escape(deal['source'])}</div>
            <div class="vcl-deal-name">{html.escape(deal['company'])}
                <span class="vcl-deal-sector">{html.escape(deal['sector'])}</span></div>
            <div class="vcl-deal-amount">{html.escape(deal['amount'])}</div>
            <div class="vcl-deal-body">{html.escape(deal['title'])}</div>
        </a>
    """


def weekly_deal_html(deal: dict) -> str:
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


def simulator_invite(company: str, key: str) -> None:
    c1, c2 = st.columns([2.6, 1.4])
    c1.caption(f"Interested in analyzing {company}? Try your own due diligence in the simulator.")
    if c2.button("Try the simulator →", key=key, use_container_width=True):
        st.session_state["prefill_company"] = company
        st.switch_page("pages/1_Startup_Screening.py")


# ---------------------------------------------------------------- page

st.markdown(
    f"""
    <div class="vcl-topbar">
        <span class="vcl-topbar-bio"><strong style="color:#14171F;">Tanmay Gambhir</strong> · Bocconi x ESSEC · Graduating 2028</span>
        <a href="{LINKEDIN_URL}" target="_blank">LinkedIn</a>
        <a href="{GITHUB_URL}" target="_blank">GitHub</a>
        <a href="{SUBSTACK_URL}" target="_blank">Substack</a>
    </div>
    """,
    unsafe_allow_html=True,
)

landing_header()

c1, c2, _ = st.columns([1.3, 1.1, 3])
with c1:
    if st.button("Open the Simulator", type="primary", use_container_width=True):
        st.switch_page("pages/0_Dashboard.py")
with c2:
    if st.button("All VC News", use_container_width=True):
        st.switch_page("pages/6_VC_Pulse.py")

with st.spinner("Pulling today's headlines..."):
    groups, _dead = fetch_all_feeds()
mixed = interleave(groups)
deals = extract_deals([item for group in groups for item in group])

section_title("Today's VC Brief", "The latest from TechCrunch, Crunchbase, Axios, Sifted, and EU-Startups.")
if mixed:
    for row_start in range(0, 6, 3):
        cols = st.columns(3)
        for col, item in zip(cols, mixed[row_start:row_start + 3]):
            with col:
                st.markdown(news_line(item), unsafe_allow_html=True)
else:
    st.caption("Feeds are unreachable right now — try again in a minute.")

if deals:
    section_title("Deal Radar", "Funding rounds detected in today's news.")
    show = deals[:6]
    for row_start in range(0, len(show), 3):
        cols = st.columns(3)
        for col, deal in zip(cols, show[row_start:row_start + 3]):
            with col:
                st.markdown(deal_card_html(deal), unsafe_allow_html=True)
    simulator_invite(show[0]["company"], "radar_sim")

picks = load_weekly_picks()
if picks.get("stale"):
    picks = {**picks, "deals": [], "videos": [], "articles": []}
if picks.get("deals"):
    section_title("This Week's Picks", f"Hand-picked deals worth studying · Week of {picks.get('week_of', '')}")
    weekly = picks["deals"]
    for row_start in range(0, len(weekly), 2):
        cols = st.columns(2)
        for col, deal in zip(cols, weekly[row_start:row_start + 2]):
            with col:
                st.markdown(weekly_deal_html(deal), unsafe_allow_html=True)
    simulator_invite(weekly[0]["company"], "weekly_sim")

section_title("Spotlight of the Week", "One video and one read, hand-picked every week.")


def spotlight_row(kicker: str, entries: list[dict]) -> None:
    items = "".join(
        f'<div class="vcl-card-title"><a href="{html.escape(e["url"])}" target="_blank" '
        f'style="color:#141B2E; text-decoration:none;">{html.escape(e["title"])}</a></div>'
        f'<div class="vcl-card-body">{html.escape(e.get("why", ""))}</div>'
        for e in entries
    ) or '<div class="vcl-card-body">Coming this week.</div>'
    st.markdown(
        f'<div class="vcl-card" style="margin-bottom:14px;"><div class="vcl-card-kicker">{kicker}</div>{items}</div>',
        unsafe_allow_html=True,
    )


spotlight_row("🎥 Video of the Week", picks.get("videos", []))
spotlight_row("📄 Article of the Week", picks.get("articles", []))

latest_post = latest_substack_post()
if latest_post:
    spotlight_row("✍️ Latest from my Substack", [{"title": latest_post["title"], "url": latest_post["link"], "why": ""}])

spotlight_row(
    "📗 Case Study",
    [{
        "title": "Bending Spoons' $18.4B IPO, run through this simulator",
        "url": "https://github.com/tanmaygambhir37-design/VC-Playbook/blob/main/reports/case-study-bending-spoons.md",
        "why": "The comps module landed within 4% of the actual IPO pricing — and the seed-stage scorecard honestly said 'Watch'.",
    }],
)

footer()
