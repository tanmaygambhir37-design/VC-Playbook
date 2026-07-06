import os
import sys

import streamlit as st

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(APP_DIR)
sys.path.append(APP_DIR)
sys.path.append(PROJECT_ROOT)
from components.cards import feature_card, text_card
from components.footer import footer
from components.navigation import sidebar
from components.theme import SUBTITLE, TAGLINE, apply_theme, page_header, section_title

st.set_page_config(page_title="About VC-Lab | VC-Lab", page_icon="🚀", layout="wide")
apply_theme()
sidebar()

page_header("About VC-Lab", SUBTITLE, "Settings")

section_title("Platform", TAGLINE)
text_card(
    "What VC-Lab Does",
    "VC-Lab is an interactive venture capital due diligence platform for evaluating startups, modeling valuation and dilution, projecting returns, and preparing investment memos.",
    "Overview",
)

section_title("Workspace Areas", "The application is organized around the workflow of a professional venture investor.")
c1, c2, c3 = st.columns(3)
with c1:
    feature_card("Analysis", "Startup screening, market context, and early diligence signals.", "search")
with c2:
    feature_card("Models", "Valuation, cap table, and portfolio return modeling.", "calculator")
with c3:
    feature_card("Reports", "Investment memo generation and future reporting surfaces.", "file-text")

section_title("Methodology", "The existing formulas remain in the model layer.")
text_card(
    "Preserved Logic",
    "Scoring, valuation, dilution, and returns calculations continue to run through the existing modules in the models directory. The redesign changes structure, navigation, and interface presentation only.",
    "Technical Note",
)

footer()
