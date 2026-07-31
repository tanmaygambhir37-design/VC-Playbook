import html

import streamlit as st

from .icons import icon

_RECOMMENDATION_COLORS = {"Proceed": "#10B981", "Watch": "#F59E0B", "Pass": "#EF4444"}


def metric_card(title: str, value: str, detail: str, icon_name: str = "activity") -> None:
    st.markdown(
        f"""
        <div class="vcl-card">
            <div class="vcl-icon">{icon(icon_name)}</div>
            <div class="vcl-metric-value">{value}</div>
            <div class="vcl-card-title">{title}</div>
            <div class="vcl-card-body">{detail}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def feature_card(title: str, description: str, icon_name: str = "activity") -> None:
    st.markdown(
        f"""
        <div class="vcl-card">
            <div class="vcl-icon">{icon(icon_name)}</div>
            <div class="vcl-card-title">{title}</div>
            <div class="vcl-card-body">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def workflow_step(number: int, title: str, description: str, icon_name: str = "activity") -> None:
    st.markdown(
        f"""
        <div class="vcl-card vcl-workflow-step">
            <div class="vcl-step-number">STEP {number:02d}</div>
            <div class="vcl-icon">{icon(icon_name)}</div>
            <div class="vcl-card-title">{title}</div>
            <div class="vcl-card-body">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def text_card(title: str, body: str, kicker: str = "") -> None:
    kicker_html = f'<div class="vcl-card-kicker">{kicker}</div>' if kicker else ""
    st.markdown(
        f"""
        <div class="vcl-card">
            {kicker_html}
            <div class="vcl-card-title">{title}</div>
            <div class="vcl-card-body">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def pill(label: str) -> str:
    return f'<span class="vcl-pill">{label}</span>'


def prefill_banner(deal: dict, assumed: list) -> None:
    """Explain a news-prefilled profile before the reader trusts its score.

    A headline reports a company, a round, and an amount. Everything else on
    the screening form is a stage benchmark standing in for a number nobody
    published, and saying so is the difference between a teaching tool and a
    machine that makes up financials.
    """
    headline = " · ".join(
        html.escape(str(deal[key]))
        for key in ("company", "round", "amount", "sector")
        if deal.get(key)
    )
    known = []
    for label, key in (("Lead", "lead"), ("Investors", "investors")):
        if deal.get(key):
            known.append(f"<strong>{label}:</strong> {html.escape(str(deal[key]))}")
    if deal.get("note"):
        known.append(html.escape(str(deal["note"])))
    source = (
        f'<a href="{html.escape(str(deal["link"]))}" target="_blank" style="color:#8A6420;">'
        "Read the source article →</a>"
        if deal.get("link") else ""
    )

    st.markdown(
        f"""
        <div class="vcl-card" style="border-left:3px solid var(--vcl-gold); margin-bottom:18px;">
            <div class="vcl-card-kicker">Prefilled from the news</div>
            <div class="vcl-card-title">{headline}</div>
            <div class="vcl-card-body" style="margin-top:6px;">{"<br>".join(known)}</div>
            <div class="vcl-card-body" style="margin-top:12px; padding-top:12px;
                 border-top:1px solid var(--vcl-border);">
                <strong>The scorecard below is a starting point, not a fact.</strong>
                Only the company, sector, and round come from the news.
                {html.escape(", ".join(assumed))} are stage-typical benchmarks standing in
                for figures nobody published — open <em>Adjust Screening Assumptions</em> and
                overwrite anything the article actually tells you.
            </div>
            <div class="vcl-card-body" style="margin-top:10px;">{source}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def deal_banner(company: str, sector: str, stage: str, vc_score: float, recommendation: str) -> None:
    color = _RECOMMENDATION_COLORS.get(recommendation, "#94A3B8")
    st.markdown(
        f"""
        <div class="vcl-deal-banner">
            <span class="vcl-deal-tag">Active Deal</span>
            <span class="vcl-deal-company">{html.escape(str(company))}</span>
            <span class="vcl-deal-dot">&middot;</span>
            <span class="vcl-deal-meta">{html.escape(str(stage))}</span>
            <span class="vcl-deal-dot">&middot;</span>
            <span class="vcl-deal-meta">{html.escape(str(sector))}</span>
            <span class="vcl-deal-dot">&middot;</span>
            <span class="vcl-deal-score" style="color:{color};">VC Score {vc_score:.1f}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def recommendation_banner(recommendation: str, vc_score: float) -> None:
    color = _RECOMMENDATION_COLORS.get(recommendation, "#94A3B8")
    st.markdown(
        f"""
        <div class="vcl-rec-banner" style="background: {color}1A; border-color: {color};">
            <span class="vcl-rec-dot" style="background:{color};"></span>
            <span class="vcl-rec-text" style="color:{color};">{html.escape(str(recommendation).upper())}</span>
            <span class="vcl-rec-score">VC Score {vc_score:.1f}/100</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
