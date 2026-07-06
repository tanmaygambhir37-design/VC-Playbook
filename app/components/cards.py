import streamlit as st

from .icons import icon


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
