import os
import sys

import streamlit as st

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(APP_DIR)
sys.path.append(APP_DIR)
sys.path.append(PROJECT_ROOT)
from components.cards import feature_card, text_card
from components.navigation import nav_link, sidebar
from components.theme import apply_theme, page_header, section_title

st.set_page_config(page_title="Future Reports | VC-Lab", page_icon="🚀", layout="wide")
apply_theme()
sidebar()

page_header("Future Reports", "A reporting roadmap for a fuller investment committee workflow.", "Reports")

section_title("Report Library", "Planned report surfaces for the next version of VC-Lab.")
cols = st.columns(3)
reports = [
    ("Sector Brief", "A concise market map with sector benchmarks, stage mix, and competitive intensity.", "bar-chart"),
    ("Deal Tearsheet", "One-page company summary with scorecard, valuation, ownership, and return views.", "file-text"),
    ("Portfolio Review", "Fund-level view of pipeline quality, return scenarios, and memo status.", "layout-dashboard"),
]
for col, report in zip(cols, reports):
    with col:
        feature_card(*report)

section_title("Current Reports", "Available today in the workspace.")
text_card(
    "Investment Memo Generator",
    "Use the Investment Memo module to create a structured thesis, risk assessment, valuation summary, and recommendation for any company in the startup dataset.",
    "Live Module",
)
nav_link("pages/5_Investment_Memo.py", label="Open Investment Memo", icon=":material/description:", use_container_width=True)
