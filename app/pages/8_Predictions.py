"""Predictions Ledger — a public, timestamped track record of calls,
resolved honestly. Data lives in data/predictions.json."""

import html
import os
import sys

import streamlit as st

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(APP_DIR)
sys.path.append(APP_DIR)
sys.path.append(PROJECT_ROOT)
from components.cards import metric_card
from components.footer import footer
from components.navigation import sidebar
from components.theme import apply_theme, page_header, section_title
from services.news import load_predictions, prediction_scorecard

st.set_page_config(page_title="Predictions | VC Playbook", page_icon="📗", layout="wide")
apply_theme()
sidebar()

page_header(
    "Predictions Ledger",
    "Public, timestamped calls — resolved honestly, misses included. A track record is the only thing that separates a view from a guess.",
    "Track Record",
)

preds = load_predictions()
stats = prediction_scorecard(preds)

_BADGE = {
    "correct": ("#3D6B5C", "✓ Correct"),
    "wrong": ("#B91C1C", "✗ Wrong"),
    "partial": ("#A9792C", "◐ Partial"),
    "open": ("#141B2E", "● Open"),
}


def prediction_card(p: dict) -> str:
    color, label = _BADGE.get(p.get("status", "open"), _BADGE["open"])
    resolution = ""
    if p.get("resolution"):
        resolution = (
            f'<div style="margin-top:10px; padding-top:10px; border-top:1px solid var(--vcl-border);'
            f' color:var(--vcl-muted); font-size:0.9rem;"><strong>Resolved {html.escape(p.get("resolved_date",""))}:</strong> '
            f'{html.escape(p["resolution"])}</div>'
        )
    return f"""
        <div class="vcl-card" style="margin-bottom:14px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span class="vcl-news-source">{html.escape(p.get('date',''))} · {html.escape(p.get('conviction',''))} conviction</span>
                <span style="background:{color}; color:#fff; font-size:0.72rem; font-weight:700;
                    padding:3px 10px; border-radius:999px; font-family:'IBM Plex Mono',monospace;">{label}</span>
            </div>
            <div class="vcl-card-title">{html.escape(p.get('subject',''))}</div>
            <div class="vcl-card-body" style="margin-top:4px;"><strong>{html.escape(p.get('claim',''))}</strong></div>
            <div class="vcl-card-body" style="margin-top:8px;">{html.escape(p.get('reasoning',''))}</div>
            <div style="color:var(--vcl-muted); font-size:0.82rem; margin-top:8px;">Resolve by {html.escape(p.get('resolve_by',''))}</div>
            {resolution}
        </div>
    """


if not preds:
    st.info("No predictions logged yet.")
else:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Calls Made", str(stats["total"]), "Total predictions logged.", "target")
    with c2:
        metric_card("Resolved", str(stats["resolved"]), "Outcomes now known.", "gauge")
    with c3:
        hit = f"{stats['hit_rate']}%" if stats["hit_rate"] is not None else "—"
        metric_card("Hit Rate", hit, "Correct ÷ resolved (partial = half).", "activity")
    with c4:
        metric_card("Open", str(stats["open"]), "Still playing out.", "circle-dollar")

    open_preds = [p for p in preds if p.get("status") == "open"]
    resolved_preds = [p for p in preds if p.get("status") != "open"]

    if open_preds:
        section_title("Open Calls", "Live predictions, not yet resolved.")
        for p in open_preds:
            st.markdown(prediction_card(p), unsafe_allow_html=True)

    if resolved_preds:
        section_title("Resolved", "How the calls actually played out.")
        for p in resolved_preds:
            st.markdown(prediction_card(p), unsafe_allow_html=True)

section_title("Why This Page Exists", "")
st.markdown(
    '<div class="vcl-card"><div class="vcl-card-body">Anyone can have opinions about startups. '
    "A dated, public ledger that scores itself — including the misses — is the honest version: it shows "
    "whether the thinking actually holds up. That is the same discipline an investment committee applies to "
    "its own memos.</div></div>",
    unsafe_allow_html=True,
)

footer()
