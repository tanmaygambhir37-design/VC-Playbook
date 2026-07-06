import os
import sys

import pandas as pd
import streamlit as st

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(APP_DIR)
sys.path.append(APP_DIR)
sys.path.append(PROJECT_ROOT)
from components.cards import metric_card, text_card
from components.navigation import sidebar
from components.theme import apply_theme, page_header, section_title
from models.scoring import score_startup
from models.valuation import comparable_multiples

st.set_page_config(page_title="Investment Memo | VC-Lab", page_icon="🚀", layout="wide")
apply_theme()
sidebar()

page_header("Investment Memo", "One click turns a screened startup into a structured investment memo.", "Reports")

DATA_PATH = os.path.join(PROJECT_ROOT, "data", "startups.csv")
df = pd.read_csv(DATA_PATH)

section_title("Memo Setup", "Choose a screened company and generate a committee-ready memo draft.")
company = st.selectbox("Select a company", df["company"])
row = df[df["company"] == company].iloc[0].to_dict()

if st.button("Generate Investment Memo", type="primary"):
    result = score_startup(row)
    val = comparable_multiples(row["revenue_usd_k"] / 1000, row["sector_median_arr_multiple"])
    ltv_cac = round(row["ltv_usd"] / row["cac_usd"], 2) if row["cac_usd"] else 0

    section_title(f"Investment Memo - {row['company']}", f"{row['sector']} · {row['stage']} · Prepared by VC-Lab")

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("VC Score", f"{result.total}/100", "Weighted diligence score.", "gauge")
    with c2:
        metric_card("Recommendation", result.recommendation, "Investment committee posture.", "target")
    with c3:
        metric_card("Adjusted Valuation", f"${val['adjusted_valuation']}M", "Comparable ARR multiple after discount.", "circle-dollar")

    st.subheader("1. Investment Thesis")
    st.markdown(
        f"{row['company']} is a {row['stage'].lower()}-stage {row['sector']} company "
        f"growing revenue at **{row['mom_growth_pct']}% month-over-month**, with an "
        f"LTV:CAC ratio of **{ltv_cac}x**. Competitive intensity in the space is "
        f"assessed as **{row['competition']}**, and the founding team scores "
        f"**{row['founder_experience_score']}/10** on prior relevant experience "
        f"across a team of {row['team_size']}."
    )

    st.subheader("2. Key Risks")
    risks = []
    if ltv_cac < 3:
        risks.append(f"Unit economics are below the 3x LTV:CAC benchmark ({ltv_cac}x), raising questions about payback efficiency at scale.")
    if row["runway_months"] < 9:
        risks.append(f"Runway of {row['runway_months']} months is short; a follow-on raise will likely be needed within two quarters.")
    if row["competition"] == "High":
        risks.append("Competitive intensity is high, which may compress pricing power and increase CAC over time.")
    if row["mom_growth_pct"] < 8 and row["stage"] != "Pre-Seed":
        risks.append("Growth rate is modest for the stage, suggesting either market saturation or a go-to-market issue.")
    if not risks:
        risks.append("No major red flags identified in the current dataset; standard execution and market risk apply.")
    for r in risks:
        st.markdown(f"- {r}")

    st.subheader("3. Valuation")
    st.markdown(
        f"Using comparable ARR multiples for {row['sector']} "
        f"({row['sector_median_arr_multiple']}x), and applying a 20% early-stage "
        f"illiquidity discount, the estimated valuation range is:"
    )
    m1, m2 = st.columns(2)
    with m1:
        metric_card("Raw ARR-Multiple Valuation", f"${val['raw_valuation']}M", "Revenue multiple before discount.", "bar-chart")
    with m2:
        metric_card("Illiquidity-Adjusted Valuation", f"${val['adjusted_valuation']}M", "Early-stage adjusted estimate.", "circle-dollar")

    st.subheader("4. Recommendation")
    text_card(
        f"VC Score: {result.total}/100 - {result.recommendation}",
        "Strengths: "
        + (", ".join(result.strengths) if result.strengths else "none flagged")
        + "<br>Weaknesses: "
        + (", ".join(result.weaknesses) if result.weaknesses else "none flagged"),
        "Decision",
    )

    memo_text = f"""INVESTMENT MEMO - {row['company']}
{row['sector']} | {row['stage']}

1. INVESTMENT THESIS
{row['company']} is a {row['stage'].lower()}-stage {row['sector']} company growing revenue at {row['mom_growth_pct']}% MoM, with an LTV:CAC ratio of {ltv_cac}x. Competition is assessed as {row['competition']}. Founding team scores {row['founder_experience_score']}/10 across a team of {row['team_size']}.

2. KEY RISKS
{chr(10).join('- ' + r for r in risks)}

3. VALUATION
Raw ARR-multiple valuation: ${val['raw_valuation']}M
Illiquidity-adjusted valuation: ${val['adjusted_valuation']}M

4. RECOMMENDATION
VC Score: {result.total}/100 - {result.recommendation}
Strengths: {', '.join(result.strengths) if result.strengths else 'none flagged'}
Weaknesses: {', '.join(result.weaknesses) if result.weaknesses else 'none flagged'}
"""
    st.download_button("Download Memo (.txt)", memo_text, file_name=f"{row['company']}_Investment_Memo.txt")
else:
    text_card(
        "Memo Studio",
        "Select a company and generate a memo to view thesis, key risks, valuation range, recommendation, and download-ready text.",
        "Ready",
    )
