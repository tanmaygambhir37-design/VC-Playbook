import os
import sys

import pandas as pd
import streamlit as st

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(APP_DIR)
sys.path.append(APP_DIR)
sys.path.append(PROJECT_ROOT)
from components.cards import feature_card, metric_card, preview_card, workflow_step
from components.footer import footer
from components.theme import GITHUB_URL, apply_theme, landing_header, section_title
from models.scoring import score_startup

st.set_page_config(page_title="VC-Lab", page_icon="🚀", layout="wide", initial_sidebar_state="collapsed")
apply_theme()

DATA_PATH = os.path.join(PROJECT_ROOT, "data", "startups.csv")


@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)


def scored_dataset():
    df = load_data()
    scores = df.apply(lambda r: score_startup(r.to_dict()).total, axis=1)
    recommendations = df.apply(lambda r: score_startup(r.to_dict()).recommendation, axis=1)
    return df.assign(vc_score=scores, recommendation=recommendations)


def landing_page() -> None:
    landing_header()

    c1, c2, _ = st.columns([1.15, 1, 3.6])
    with c1:
        if st.button("Launch Workspace", type="primary", use_container_width=True):
            st.switch_page("pages/0_Dashboard.py")
    with c2:
        st.link_button("View GitHub", GITHUB_URL, use_container_width=True)

    df_scored = scored_dataset()

    section_title("Platform Metrics", "A professional diligence workspace for screening, modeling, and memo generation.")
    cols = st.columns(4)
    metrics = [
        ("Companies Analysed", f"{len(df_scored)}", "Synthetic startup profiles across sectors and stages.", "building"),
        ("Investment Memos", "12", "Structured committee-ready memo outputs.", "file-text"),
        ("Valuation Models", "3", "VC Method, comparables, and scorecard valuation.", "calculator"),
        ("Interactive Dashboards", "6", "Screening, market, valuation, cap table, returns, memo.", "layout-dashboard"),
    ]
    for col, item in zip(cols, metrics):
        with col:
            metric_card(*item)

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

    section_title("Workspace Preview", "Modern module previews for the diligence flow.")
    preview_cols = st.columns(3)
    previews = [
        ("Screening Dashboard", "Rank companies by VC score and recommendation."),
        ("Valuation Workspace", "Compare model outputs with live assumptions."),
        ("Memo Studio", "Generate thesis, risk, valuation, and recommendation sections."),
    ]
    for col, item in zip(preview_cols, previews):
        with col:
            preview_card(*item)

    footer()


landing_page()
