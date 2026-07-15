import os
import sys

import streamlit as st

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(APP_DIR)
sys.path.append(APP_DIR)
sys.path.append(PROJECT_ROOT)
from components.cards import deal_banner, metric_card, text_card
from components.navigation import sidebar
from components.theme import apply_theme, page_header, section_title
from models.scoring import score_startup
from models.returns import irr_from_moic
from models.valuation import SCORECARD_FACTORS, comparable_multiples, scorecard_method, vc_method
from state import deal_widget_key, get_active_deal_row

# Typical share of ownership retained through future dilution, by entry stage
STAGE_RETENTION = {"Pre-Seed": 40, "Seed": 50, "Series A": 65, "Series B": 80, "Growth": 85}

st.set_page_config(page_title="Valuation | VC Playbook", page_icon="📗", layout="wide")
apply_theme()
sidebar()

page_header("Valuation", "Three complementary early-stage valuation methods, side by side.", "Analysis")

active_deal = get_active_deal_row()
if active_deal:
    deal_score = score_startup(active_deal)
    deal_banner(active_deal["company"], active_deal["sector"], active_deal["stage"], deal_score.total, deal_score.recommendation)
    default_arr = round(min(max(active_deal.get("revenue_usd_k", 2000) / 1000, 0.1), 50.0), 2)
    default_multiple = int(round(min(max(active_deal.get("sector_median_arr_multiple", 8), 2), 25)))
    default_stage = active_deal.get("stage") if active_deal.get("stage") in STAGE_RETENTION else "Seed"
else:
    default_arr, default_multiple, default_stage = 2.0, 8, "Seed"

tab1, tab2, tab3 = st.tabs(["VC Method", "Comparable Multiples", "Scorecard Method"])

with tab1:
    section_title("VC Method", "Back-solves today's valuation from a target exit outcome and required return.")
    stage_options = list(STAGE_RETENTION.keys())
    c0, c1, c2, c3 = st.columns(4)
    entry_stage = c0.selectbox(
        "Entry Stage",
        stage_options,
        index=stage_options.index(default_stage),
        help="Sets a stage-appropriate default for retention through future dilution.",
    )
    exit_value = c1.slider("Projected Exit Value ($M)", 10, 2000, 300, step=10)
    target_multiple = c2.slider("Required Return Multiple (x)", 2, 30, 10)
    investment = c3.slider("Investment Amount ($M)", 0.1, 20.0, 2.0, step=0.1)
    stage_default_retention = STAGE_RETENTION[entry_stage]
    retention = st.slider(
        "Retention Through Future Rounds (%)", 30, 100, stage_default_retention, step=5,
        key=f"vc_method_retention_{entry_stage}",
        help=(
            "Share of today's ownership the investor still holds at exit after future dilution. "
            f"Default for {entry_stage} is {stage_default_retention}%. "
            "Typical: Pre-Seed ~40%, Seed ~50%, Series A ~65%, Series B ~80%, Growth ~85%."
        ),
    )

    res = vc_method(exit_value, target_multiple, investment, retention / 100)
    hold_years = st.slider("Holding Period (years)", 3, 12, 7)
    implied_irr = irr_from_moic(target_multiple, hold_years)
    st.caption(
        f"Sanity check: ${investment}M in at ${res.pre_money}M pre, exiting at ${exit_value}M "
        f"in {hold_years} years returns your {target_multiple}x target — a {implied_irr}% IRR."
    )
    m1, m2, m3 = st.columns(3)
    with m1:
        metric_card("Post-Money Valuation", f"${res.post_money}M", "Implied current post-money valuation.", "circle-dollar")
    with m2:
        metric_card("Pre-Money Valuation", f"${res.pre_money}M", "Implied current pre-money valuation.", "calculator")
    with m3:
        metric_card("Investor Ownership", f"{res.investor_ownership_pct}%", "Ownership required to hit target return.", "target")

with tab2:
    section_title("Comparable Multiples", "Values the company as a multiple of ARR, benchmarked to sector comparables.")
    c1, c2, c3 = st.columns(3)
    arr = c1.slider("Current ARR ($M)", 0.1, 50.0, default_arr, step=0.1, key=deal_widget_key("arr"))
    multiple = c2.slider("Sector ARR Multiple (x)", 2, 25, default_multiple, key=deal_widget_key("multiple"))
    discount = c3.slider("Illiquidity Discount (%)", 0, 50, 20)

    res2 = comparable_multiples(arr, multiple, discount)
    m1, m2 = st.columns(2)
    with m1:
        metric_card("Raw Valuation", f"${res2['raw_valuation']}M", "ARR multiplied by sector benchmark.", "bar-chart")
    with m2:
        metric_card("Adjusted Valuation", f"${res2['adjusted_valuation']}M", "Valuation after early-stage discount.", "circle-dollar")

with tab3:
    section_title("Scorecard Method", "Adjusts a regional median pre-money using qualitative deal factors.")
    median_pre = st.slider("Median Regional Pre-Money ($M)", 1.0, 20.0, 5.0, step=0.5)

    st.markdown("Rate each factor vs. a typical deal, where 100 is average.")
    factor_scores = {}
    cols = st.columns(len(SCORECARD_FACTORS))
    for col, (key, weight) in zip(cols, SCORECARD_FACTORS.items()):
        label = key.replace("_", " ").title()
        factor_scores[key] = col.slider(f"{label} ({int(weight*100)}%)", 50, 200, 100, step=5, key=key)

    res3 = scorecard_method(median_pre, factor_scores)
    m1, m2 = st.columns(2)
    with m1:
        metric_card("Adjustment Factor", f"{res3['adjustment_factor']}x", "Weighted qualitative uplift or discount.", "activity")
    with m2:
        metric_card("Adjusted Pre-Money", f"${res3['adjusted_pre_money']}M", "Pre-money after scorecard factors.", "circle-dollar")

section_title("Investor Context", "How to read the outputs.")
text_card(
    "Triangulation",
    "In practice, VCs triangulate across all three methods: the VC Method anchors to expected fund returns, comparables ground the number in the current market, and the Scorecard Method captures qualitative diligence.",
    "Methodology",
)
