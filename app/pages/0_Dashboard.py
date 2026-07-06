import os
import sys

import pandas as pd
import streamlit as st

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(APP_DIR)
sys.path.append(APP_DIR)
sys.path.append(PROJECT_ROOT)
from components.cards import feature_card, metric_card, text_card
from components.navigation import nav_link, sidebar
from components.theme import TAGLINE, apply_theme, page_header, section_title
from models.scoring import score_startup

st.set_page_config(page_title="Dashboard | VC-Lab", page_icon="🚀", layout="wide")
apply_theme()
sidebar()

DATA_PATH = os.path.join(PROJECT_ROOT, "data", "startups.csv")


@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)


df = load_data()
scores = df.apply(lambda r: score_startup(r.to_dict()).total, axis=1)
recommendations = df.apply(lambda r: score_startup(r.to_dict()).recommendation, axis=1)
df_scored = df.assign(vc_score=scores, recommendation=recommendations)
avg_score = df_scored["vc_score"].mean()
recommended = int((df_scored["vc_score"] >= 75).sum())

page_header("Dashboard", "Professional Venture Capital Workspace")

cols = st.columns(4)
dashboard_metrics = [
    ("Recent Analyses", f"{len(df_scored)}", "Companies screened in the current dataset.", "database"),
    ("Average VC Score", f"{avg_score:.0f}", "Portfolio-wide scorecard benchmark.", "gauge"),
    ("Investment Memos Generated", "12", "Memo workflows prepared for review.", "file-text"),
    ("Portfolio IRR", "31%", "Illustrative expected return snapshot.", "line-chart"),
]
for col, item in zip(cols, dashboard_metrics):
    with col:
        metric_card(*item)

section_title("Pipeline", "Recent companies, reports, and models in one operating view.")
left, middle, right = st.columns([1.3, 1, 1])
with left:
    st.markdown('<div class="vcl-card-kicker">Recent Companies</div>', unsafe_allow_html=True)
    st.dataframe(
        df_scored[["company", "sector", "stage", "vc_score", "recommendation"]]
        .sort_values("vc_score", ascending=False)
        .head(8),
        use_container_width=True,
        hide_index=True,
    )
with middle:
    text_card(
        "Recent Reports",
        "Investment memo drafts, valuation notes, and sector snapshots prepared from the workspace.",
        "Reports",
    )
    text_card(
        "Recent Models",
        "VC Method, ARR multiple, cap table, and returns sensitivity models ready for review.",
        "Models",
    )
with right:
    text_card(
        "Investment Pipeline",
        f"{recommended} companies currently clear the Proceed threshold. Use screening before moving to valuation or memo generation.",
        "Status",
    )

section_title("Quick Actions", "Jump into the most common diligence tasks.")
q1, q2, q3, q4 = st.columns(4)
nav_link("pages/1_Startup_Screening.py", label="New Startup", icon=":material/add_circle:", use_container_width=True, container=q1)
nav_link("pages/1_Startup_Screening.py", label="Open Screening", icon=":material/troubleshoot:", use_container_width=True, container=q2)
nav_link("pages/5_Investment_Memo.py", label="Generate Memo", icon=":material/description:", use_container_width=True, container=q3)
nav_link("pages/7_Future_Reports.py", label="View Reports", icon=":material/folder_open:", use_container_width=True, container=q4)

section_title("Workspace Focus", TAGLINE)
f1, f2, f3 = st.columns(3)
with f1:
    feature_card("Analysis", "Screen startups and inspect market patterns before moving into deeper diligence.", "search")
with f2:
    feature_card("Models", "Build valuation, dilution, and return views from consistent assumptions.", "calculator")
with f3:
    feature_card("Reports", "Turn outputs into clear investment memo narratives for decision-making.", "clipboard")
