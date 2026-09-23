import os
import sys

import streamlit as st

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(APP_DIR)
sys.path.append(APP_DIR)
sys.path.append(PROJECT_ROOT)
import fresh_modules  # noqa: E402  (must run before our own imports)
fresh_modules.refresh()
from components.cards import feature_card, text_card
from components.footer import email_capture, footer
from components.navigation import sidebar
from components.theme import CASE_STUDY_PAGE, GITHUB_URL, SUBTITLE, TAGLINE, apply_theme, page_header, section_title
from services.analytics import track_page

st.set_page_config(page_title="About | VC Playbook", page_icon="📗", layout="wide")
apply_theme()
sidebar()
track_page("about", "About")

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

section_title("Case Study: Oura", "Called before the IPO priced, not after.")
text_card(
    "A pre-registered call on a live IPO",
    "Oura launched its Nasdaq IPO on Sep 22, 2026 at $40-44 a share. Before it priced, I ran its S-1 numbers "
    "through the simulator with the exact settings used for Bending Spoons, nothing re-tuned: $1.62B run-rate "
    "revenue x 8 = $12.95B ($40.36 a share), and a 66.7/100 'Watch' on the scorecard. The call and the rule "
    "for judging it are written down in advance; the model's % error gets published whatever it is. Written "
    "for beginners too, with a step-by-step IPO explainer and a plain-English glossary.",
    "Pre-Registered Call",
)
if st.button("Read the Oura case study →", key="about_oura_case"):
    st.switch_page(CASE_STUDY_PAGE, query_params={"study": "oura"})

section_title("Case Study: Bending Spoons", "A real IPO run through the simulator, end to end.")
text_card(
    "The $18.4B sanity check",
    "When Bending Spoons listed on Nasdaq (July 2026, $18.4B), I ran its disclosed numbers through this "
    "simulator: $2.4B run-rate revenue, +132% YoY, EBITDA-profitable, 4,418 people. The comps module priced "
    "it at $19.2B — within 4% of the actual IPO pricing. The seed-stage scorecard said 71/100 'Watch', which "
    "is the more interesting result: frameworks encode a stage, and watching one strain on a growth-stage "
    "profile teaches you when its assumptions apply. Full walkthrough with screenshots and the generated IC "
    "memo is linked below.",
    "Real-World Test",
)
if st.button("Read the Bending Spoons case study →", key="about_bsp_case"):
    st.switch_page(CASE_STUDY_PAGE, query_params={"study": "bending-spoons"})

section_title("Running Experiments", "Treating the site like a product, not a portfolio piece.")
text_card(
    "Landing A/B test — pre-registered",
    "One metric: the share of landing visitors who complete a valuation. One live A/B test on the hero CTA "
    "(\"explore the workspace\" vs \"value a startup in 2 minutes\"), assigned 50/50 and running two weeks. "
    "The hypothesis, metric, and decision rule were written down <em>before</em> collecting data — and the "
    "result gets published whatever it says, including \"inconclusive, too little traffic to trust,\" which "
    "for a young site is the honest and likely outcome. Pre-registration and analysis script are in the repo.",
    "Product Discipline",
)
st.link_button("Read the pre-registered experiment →", f"{GITHUB_URL}/blob/main/reports/experiment-01-landing-cta.md")

section_title("Built By", "")
text_card(
    "Tanmay Gambhir",
    "Bocconi x ESSEC double degree, graduating 2028 · Chartered Accountant · Management Consultant. "
    "Building at the intersection of finance, strategy, and AI.",
    "Author",
)

email_capture()
footer()
