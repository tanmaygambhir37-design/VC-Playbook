import html
import os
import sys

import streamlit as st

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(APP_DIR)
sys.path.append(APP_DIR)
sys.path.append(PROJECT_ROOT)
from components.footer import email_capture, footer
from components.theme import (
    CASE_STUDY_URL,
    GITHUB_URL,
    LINKEDIN_URL,
    PORTFOLIO_URL,
    RESEARCH_URL,
    SUBSTACK_URL,
    apply_theme,
    hide_sidebar,
    landing_header,
    section_title,
)
from services.analytics import track_event, track_page
from services.news import (
    extract_deals,
    fetch_all_feeds,
    interleave,
    latest_substack_post,
    load_predictions,
    load_weekly_picks,
    prediction_scorecard,
)
from state import set_prefill_deal

st.set_page_config(page_title="VC Playbook", page_icon="📗", layout="wide", initial_sidebar_state="collapsed")
apply_theme()
hide_sidebar()
track_page("home", "VC Playbook")


def news_line(item: dict) -> str:
    return f"""
        <a class="vcl-news-card" href="{html.escape(item['link'])}" target="_blank">
            <div class="vcl-news-source">{html.escape(item['source'])}</div>
            <div class="vcl-news-title">{html.escape(item['title'])}</div>
        </a>
    """


def deal_card_html(deal: dict) -> str:
    """A deal card that stays on the site.

    The source link is still here, but small — the card's job is to hand the
    deal to the simulator, not to hand the visitor to TechCrunch.
    """
    meta = " · ".join(
        html.escape(str(deal[key])) for key in ("round", "sector") if deal.get(key)
    )
    lead = f"<strong>Lead:</strong> {html.escape(deal['lead'])}<br>" if deal.get("lead") else ""
    note = html.escape(deal.get("note") or deal.get("title", ""))
    source = (
        f'<a href="{html.escape(deal["link"])}" target="_blank" '
        'style="color:#8A6420; font-size:var(--fs-xs);">Source →</a>'
        if deal.get("link") else ""
    )
    return f"""
        <div class="vcl-deal-card">
            <div class="vcl-news-source">{html.escape(deal.get('source') or deal.get('category', 'Venture'))}</div>
            <div class="vcl-deal-name">{html.escape(deal['company'])}</div>
            <div class="vcl-deal-amount">{html.escape(deal.get('amount', ''))}
                <span class="vcl-deal-sector-plain">{meta}</span></div>
            <div class="vcl-deal-body">{lead}{note}</div>
            <div style="margin-top:10px;">{source}</div>
        </div>
    """


def analyze_button(deal: dict, key: str) -> None:
    if st.button(f"Analyze {deal['company']} →", key=key, use_container_width=True):
        set_prefill_deal(deal)
        track_event("analyze_deal_clicked", company=deal.get("company"), sector=deal.get("sector"))
        st.switch_page("pages/1_Startup_Screening.py")


# ---------------------------------------------------------------- page

st.markdown(
    f"""
    <div class="vcl-topbar">
        <span class="vcl-topbar-bio"><strong style="color:#14171F;">Tanmay Gambhir</strong> · Bocconi x ESSEC · Graduating 2028</span>
        <a href="{PORTFOLIO_URL}" target="_blank">Portfolio</a>
        <a href="{RESEARCH_URL}" target="_blank">Research</a>
        <a href="{LINKEDIN_URL}" target="_blank">LinkedIn</a>
        <a href="{GITHUB_URL}" target="_blank">GitHub</a>
        <a href="{SUBSTACK_URL}" target="_blank">Substack</a>
    </div>
    """,
    unsafe_allow_html=True,
)

landing_header()

nav1, nav2, nav3, nav4 = st.columns(4)
if nav1.button("Open the Simulator", type="primary", use_container_width=True):
    track_event("cta_open_simulator", placement="hero")
    st.switch_page("pages/0_Dashboard.py")
if nav2.button("Today's VC News", use_container_width=True):
    track_event("cta_vc_pulse", placement="hero")
    st.switch_page("pages/6_VC_Pulse.py")
if nav3.button("Track Record", use_container_width=True):
    track_event("cta_predictions", placement="hero")
    st.switch_page("pages/8_Predictions.py")
if nav4.button("About", use_container_width=True):
    track_event("cta_about", placement="hero")
    st.switch_page("pages/7_About.py")

# ---------------------------------------------------------------- proof first
#
# The aggregated headlines below used to open this page. They are commodity —
# the same wire every reader already gets by email — and every card is an exit.
# What is not commodity is a public track record and a model that was checked
# against a real outcome, so those lead now.

_preds = load_predictions()
_stats = prediction_scorecard(_preds) if _preds else None

section_title("Why Trust The Output", "A model is only interesting if someone checks it against reality.")
proof_left, proof_right = st.columns(2)

with proof_left:
    st.markdown(
        """
        <div class="vcl-card vcl-card-equal" style="border-left:3px solid var(--vcl-gold);">
            <div class="vcl-card-kicker">Case Study · Real IPO</div>
            <div class="vcl-metric-value">Within 4%</div>
            <div class="vcl-card-title">Bending Spoons priced at $18.4B. This simulator said $19.2B.</div>
            <div class="vcl-card-body">
                Run on the company's disclosed numbers before pricing: $2.4B run-rate revenue,
                +132% YoY, EBITDA-profitable. The seed-stage scorecard, applied to a growth-stage
                company, honestly said "Watch" — which is the more useful lesson.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.link_button("Read the full walkthrough →", CASE_STUDY_URL, use_container_width=True)

with proof_right:
    if _stats:
        hit = f"{_stats['hit_rate']}%" if _stats["hit_rate"] is not None else "—"
        st.markdown(
            f"""
            <div class="vcl-card vcl-card-equal" style="border-left:3px solid var(--vcl-blue);">
                <div class="vcl-card-kicker">Predictions Ledger · Public</div>
                <div class="vcl-metric-value">{hit} hit rate</div>
                <div class="vcl-card-title">{_stats['total']} dated calls · {_stats['resolved']} resolved · {_stats['open']} still open</div>
                <div class="vcl-card-body">
                    Every call is timestamped before the outcome is known and scored honestly
                    afterwards, misses included. A track record is the only thing separating
                    a view from a guess.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("See every call →", key="preds_cta", use_container_width=True):
            track_event("cta_predictions", placement="proof")
            st.switch_page("pages/8_Predictions.py")

# ------------------------------------------------------- deals into simulator

picks = load_weekly_picks()

with st.spinner("Pulling today's headlines..."):
    groups, _dead = fetch_all_feeds()
mixed = interleave(groups)
radar = extract_deals([item for group in groups for item in group])

analyzable = (picks.get("deals") or [])[:3] or radar[:3]
if analyzable:
    section_title(
        "Analyze This Week's Deals",
        "One click loads the deal into the scorecard with stage-typical benchmarks — then you correct them.",
    )
    cols = st.columns(len(analyzable))
    for index, (col, deal) in enumerate(zip(cols, analyzable)):
        with col:
            st.markdown(deal_card_html(deal), unsafe_allow_html=True)
            analyze_button(deal, key=f"analyze_{index}")

# ------------------------------------------------------------- news, demoted

if mixed:
    section_title("Today's VC Brief", "The wire, in brief — TechCrunch, Crunchbase, Axios, Sifted, EU-Startups.")
    cols = st.columns(3)
    for col, item in zip(cols, mixed[:3]):
        with col:
            st.markdown(news_line(item), unsafe_allow_html=True)
    if st.button("All headlines and the full deal radar →", use_container_width=True):
        track_event("cta_vc_pulse", placement="brief")
        st.switch_page("pages/6_VC_Pulse.py")

# ---------------------------------------------------------------- spotlight


def spotlight_row(kicker: str, entries: list[dict]) -> None:
    items = "".join(
        f'<div class="vcl-card-title"><a href="{html.escape(e["url"])}" target="_blank" '
        f'style="color:#141B2E; text-decoration:none;">{html.escape(e["title"])}</a></div>'
        f'<div class="vcl-card-body">{html.escape(e.get("why", ""))}</div>'
        for e in entries
    )
    if not items:
        return
    st.markdown(
        f'<div class="vcl-card" style="margin-bottom:14px;"><div class="vcl-card-kicker">{kicker}</div>{items}</div>',
        unsafe_allow_html=True,
    )


spotlight_entries = bool(picks.get("videos") or picks.get("articles"))
latest_post = latest_substack_post()
if spotlight_entries or latest_post:
    section_title("Worth Your Time", f"Hand-picked, {picks.get('as_of_label', 'updated weekly')}.")
    spotlight_row("🎥 Video of the Week", picks.get("videos", []))
    spotlight_row("📄 Article of the Week", picks.get("articles", []))
    if latest_post:
        spotlight_row("✍️ Latest from my Substack", [{"title": latest_post["title"], "url": latest_post["link"], "why": ""}])

email_capture()
footer()
