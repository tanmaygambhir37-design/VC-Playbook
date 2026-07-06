import html

import streamlit as st

from components.cards import pill
from services.due_diligence import DueDiligenceSection


PROGRESS_ITEMS = [
    "Company Profile",
    "Business Model",
    "Market",
    "Competition",
    "Team",
    "Recommendation",
]


def _confidence_color(confidence: str) -> str:
    if confidence == "High":
        return "#10B981"
    if confidence == "Low":
        return "#EF4444"
    return "#F59E0B"


def render_due_diligence_progress() -> None:
    labels = "".join(pill(f"{item} &#10003;") for item in PROGRESS_ITEMS)
    st.markdown(
        f"""
        <div class="vcl-card">
            <div class="vcl-card-kicker">Due Diligence Progress</div>
            <div>{labels}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_due_diligence_section(section: DueDiligenceSection, expanded: bool = False) -> None:
    confidence_color = _confidence_color(section.confidence)
    source_labels = "".join(pill(html.escape(source)) for source in section.sources)
    with st.expander(section.title, expanded=expanded):
        st.markdown(
            f"""
            <div class="vcl-card">
                <div class="vcl-card-title">{html.escape(section.title)}</div>
                <div class="vcl-card-body">{html.escape(section.paragraph)}</div>
                <div style="height: 16px;"></div>
                <div class="vcl-card-kicker">Confidence</div>
                <span class="vcl-pill" style="border-color: {confidence_color}; color: {confidence_color};">
                    {html.escape(section.confidence)}
                </span>
                <div style="height: 14px;"></div>
                <div class="vcl-card-kicker">Sources</div>
                <div>{source_labels}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_due_diligence_report(sections: list[DueDiligenceSection]) -> None:
    render_due_diligence_progress()
    for index, section in enumerate(sections):
        render_due_diligence_section(section, expanded=index == 0)
