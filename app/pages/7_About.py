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

st.set_page_config(page_title="About | VC Playbook", page_icon="📗", layout="wide")
apply_theme()
sidebar()

page_header("About VC Playbook", SUBTITLE, "Settings")

section_title("What This Is", TAGLINE)
text_card(
    "An honest simulator, not a platform",
    "VC Playbook is a learning tool. The VC Pulse page aggregates real, live venture capital news; "
    "the simulator lets you practice the actual analytical workflow of an early-stage investor — "
    "screening, valuation, dilution, returns, and memo writing — on a sample dataset or your own numbers. "
    "The sample companies are synthetic and the outputs are illustrative, not investment advice.",
    "Overview",
)

section_title("Who It's For", "Two audiences, one workspace.")
c1, c2 = st.columns(2)
with c1:
    feature_card(
        "VC-curious students & juniors",
        "Get your daily VC news in one place and learn the vocabulary and mechanics of venture investing by doing.",
        "search",
    )
with c2:
    feature_card(
        "Analysts & operators",
        "Sanity-check a scorecard, a valuation triangulation, or a dilution scenario in seconds with your own inputs.",
        "calculator",
    )

section_title("Methodology", "Standard early-stage frameworks, implemented faithfully.")
text_card(
    "The models",
    "Screening uses a weighted scorecard (unit economics, growth, market, team, efficiency). "
    "Valuation triangulates the VC Method, comparable ARR multiples with an illiquidity discount, "
    "and the Bill Payne scorecard method. Cap table and returns use standard priced-round and "
    "MOIC/IRR math. All formulas live in the open-source models directory on GitHub.",
    "Technical Note",
)

section_title("Built By", "")
text_card(
    "Tanmay Gambhir",
    "Bocconi x ESSEC double degree, graduating 2028 · Chartered Accountant · Management Consultant. "
    "Building at the intersection of finance, strategy, and AI.",
    "Author",
)

footer()
