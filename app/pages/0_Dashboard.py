import os
import sys

import streamlit as st

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(APP_DIR)
sys.path.append(APP_DIR)
sys.path.append(PROJECT_ROOT)
from components.cards import text_card, workflow_step
from components.footer import footer
from components.navigation import nav_link, sidebar
from components.theme import CASE_STUDY_URL, apply_theme, page_header, section_title
from services.analytics import track_page
from services.dataset import scored_dataset
from models.scoring import score_startup
from state import get_active_deal_row

st.set_page_config(page_title="Dashboard | VC Playbook", page_icon="📗", layout="wide")
apply_theme()
sidebar()
track_page("dashboard", "Dashboard")

df_scored = scored_dataset()
recommended = int((df_scored["vc_score"] >= 75).sum())

page_header("Dashboard", "Your due diligence simulator workspace — screen a company, value it, model dilution, and generate a memo. Practice on the sample dataset or bring your own numbers.")

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
        .head(8)
        .rename(columns={
            "company": "Company", "sector": "Sector", "stage": "Stage",
            "vc_score": "VC Score", "recommendation": "Call",
        }),
        use_container_width=True,
        hide_index=True,
    )
with middle:
    # This column used to describe reports and models that did not exist. It
    # now shows the one piece of real state the workspace has: the deal the
    # visitor is actually carrying through the flow.
    active = get_active_deal_row()
    if active:
        active_result = score_startup(active)
        text_card(
            f"Active Deal — {active['company']}",
            f"{active.get('sector', '')} · {active.get('stage', '')}<br>"
            f"VC Score <strong>{active_result.total}/100</strong> · {active_result.recommendation}<br>"
            "Carry it into valuation, cap table, or the memo below.",
            "In Progress",
        )
    else:
        text_card(
            "No Active Deal Yet",
            "Screen a company — from the sample dataset, your own numbers, or a deal from "
            "the news — and it carries through valuation, cap table, and the memo without "
            "re-entering anything.",
            "Start Here",
        )
with right:
    text_card(
        "Investment Pipeline",
        f"{recommended} of {len(df_scored)} sample companies clear the Proceed threshold "
        "(VC Score 75+). Screening comes before valuation or memo generation.",
        "Status",
    )
    text_card(
        "Checked Against A Real Outcome",
        "The comps module priced Bending Spoons' IPO within 4% of its actual $18.4B pricing. "
        f'<a href="{CASE_STUDY_URL}" target="_blank" style="color:#8A6420;">Read the walkthrough →</a>',
        "Case Study",
    )

section_title("Quick Actions", "Jump into the most common diligence tasks.")
q1, q2, q3, q4 = st.columns(4)
nav_link("pages/1_Startup_Screening.py", label="New Startup", icon=":material/add_circle:", use_container_width=True, container=q1)
nav_link("pages/2_Valuation.py", label="Run Valuation", icon=":material/attach_money:", use_container_width=True, container=q2)
nav_link("pages/3_Cap_Table_Returns.py", label="Cap Table & Returns", icon=":material/account_tree:", use_container_width=True, container=q3)
nav_link("pages/4_Investment_Memo.py", label="Generate Memo", icon=":material/description:", use_container_width=True, container=q4)

footer()
