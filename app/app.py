import os
import sys

import streamlit as st

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(APP_DIR)
sys.path.append(APP_DIR)
sys.path.append(PROJECT_ROOT)
from components.cards import feature_card, workflow_step
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

st.set_page_config(page_title="VC Playbook", page_icon="📗", layout="wide", initial_sidebar_state="collapsed")
apply_theme()
hide_sidebar()


def landing_page() -> None:
    st.markdown(
        f"""
        <div class="vcl-topbar">
            <span class="vcl-topbar-bio"><strong style="color:#F8FAFC;">Tanmay Gambhir</strong> · Bocconi x ESSEC · Graduating 2028</span>
            <a href="{LINKEDIN_URL}" target="_blank">LinkedIn</a>
            <a href="{GITHUB_URL}" target="_blank">GitHub</a>
            <a href="{SUBSTACK_URL}" target="_blank">Substack</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    landing_header()

    c1, c2, c3, _ = st.columns([1.15, 1.15, 1, 2.4])
    with c1:
        if st.button("Open the Simulator", type="primary", use_container_width=True):
            st.switch_page("pages/0_Dashboard.py")
    with c2:
        if st.button("Read VC News", use_container_width=True):
            st.switch_page("pages/7_VC_Pulse.py")
    with c3:
        st.link_button("View GitHub", GITHUB_URL, use_container_width=True)

    section_title("What is VC Playbook?", "Two things, honestly labeled — no fake metrics.")
    w1, w2 = st.columns(2)
    with w1:
        feature_card(
            "A VC news hub",
            "A live feed pulling the latest venture capital news from TechCrunch, Crunchbase News, "
            "Axios, and more — plus curated videos and articles. Built for students, analysts, and "
            "juniors who want one place to stay current on the industry.",
            "bar-chart",
        )
    with w2:
        feature_card(
            "A due diligence simulator",
            "An interactive sandbox that walks you through how professional investors evaluate "
            "startups: weighted scorecards, three valuation methods, cap table dilution, fund "
            "returns, and auto-drafted investment memos. Try your own diligence — on the sample "
            "dataset or your own numbers.",
            "target",
        )

    section_title("Workflow", "Move from first-pass screen to investment committee memo in one connected flow.")
    workflow = [
        ("Startup Screening", "Score traction, team, market, and efficiency.", "search"),
        ("Market Analysis", "Compare sectors, stages, and competitive intensity.", "bar-chart"),
        ("Valuation", "Triangulate early-stage valuation ranges.", "circle-dollar"),
        ("Cap Table", "Model priced rounds and ownership dilution.", "network"),
        ("Portfolio Returns", "Stress-test MOIC and IRR outcomes.", "line-chart"),
        ("Investment Memo", "Generate a structured diligence memo.", "clipboard"),
    ]
    for row_start in range(0, len(workflow), 3):
        cols = st.columns(3)
        for offset, col in enumerate(cols):
            title, description, icon_name = workflow[row_start + offset]
            with col:
                workflow_step(row_start + offset + 1, title, description, icon_name)

    section_title("Analysis Modules", "Each module behaves like a workspace surface, not a detached calculator.")
    features = [
        ("Startup Screening", "Weighted VC scorecard across unit economics, growth, market, team, and efficiency.", "target"),
        ("Market Sizing", "Sector and stage views that help frame opportunity quality before deeper modeling.", "bar-chart"),
        ("Valuation Engine", "Run VC Method, comparable multiples, and scorecard valuation side by side.", "calculator"),
        ("Cap Table Simulator", "Model founder, ESOP, and investor ownership through sequential rounds.", "network"),
        ("Portfolio Returns", "Translate investment size, ownership, exit value, and hold period into fund returns.", "line-chart"),
        ("Investment Memo Generator", "Turn screened companies into concise, downloadable investment committee notes.", "file-text"),
    ]
    for row_start in range(0, len(features), 3):
        cols = st.columns(3)
        for offset, col in enumerate(cols):
            with col:
                feature_card(*features[row_start + offset])

    footer()


landing_page()
