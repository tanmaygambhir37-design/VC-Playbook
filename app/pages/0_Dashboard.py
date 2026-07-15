import os
import sys

import pandas as pd
import streamlit as st

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(APP_DIR)
sys.path.append(APP_DIR)
sys.path.append(PROJECT_ROOT)
from components.cards import metric_card, text_card, workflow_step
from components.navigation import nav_link, sidebar
from components.theme import apply_theme, page_header, section_title
from models.scoring import score_startup

st.set_page_config(page_title="Dashboard | VC Playbook", page_icon="📗", layout="wide")
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

page_header("Dashboard", "Your due diligence simulator workspace. Everything below is computed live from the sample dataset — screen a company, value it, model dilution, and generate a memo.")

cols = st.columns(4)
dashboard_metrics = [
    ("Sample Companies", f"{len(df_scored)}", "Synthetic startup profiles loaded in the dataset.", "database"),
    ("Average VC Score", f"{avg_score:.0f}", "Scorecard benchmark across the dataset.", "gauge"),
    ("Clear the Proceed Bar", f"{recommended}", "Companies scoring 75+ on the weighted scorecard.", "target"),
    ("Sectors Covered", f"{df_scored['sector'].nunique()}", "Industries represented in the sample set.", "bar-chart"),
]
for col, item in zip(cols, dashboard_metrics):
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
    wcols = st.columns(3)
    for offset, wcol in enumerate(wcols):
        wtitle, wdesc, wicon = workflow[row_start + offset]
        with wcol:
            workflow_step(row_start + offset + 1, wtitle, wdesc, wicon)

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
nav_link("pages/2_Valuation.py", label="Run Valuation", icon=":material/attach_money:", use_container_width=True, container=q2)
nav_link("pages/3_Cap_Table_Returns.py", label="Cap Table & Returns", icon=":material/account_tree:", use_container_width=True, container=q3)
nav_link("pages/5_Investment_Memo.py", label="Generate Memo", icon=":material/description:", use_container_width=True, container=q4)
