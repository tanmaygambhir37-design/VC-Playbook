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


def preview_card(title: str, description: str) -> None:
    st.markdown(
        f"""
        <div class="vcl-preview">
            <div class="vcl-card-title">{title}</div>
            <div class="vcl-card-body">{description}</div>
            <div class="vcl-preview-bar long"></div>
            <div class="vcl-preview-bar short"></div>
            <div class="vcl-preview-chart"></div>
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
