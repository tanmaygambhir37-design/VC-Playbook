import os
import sys

import pandas as pd
import streamlit as st

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(APP_DIR)
sys.path.append(APP_DIR)
sys.path.append(PROJECT_ROOT)
from components.cards import metric_card, recommendation_banner, text_card
from components.due_diligence import render_due_diligence_section
from components.navigation import sidebar
from components.theme import apply_theme, page_header, section_title
from models.scoring import score_startup
from models.valuation import comparable_multiples
from services.due_diligence import (
    generate_business_model,
    generate_competition,
    generate_confidence_score,
    generate_executive_summary,
    generate_market,
    generate_problem,
    generate_solution,
)
from services.pdf_report import build_memo_pdf
from state import get_active_deal_parsed, get_active_deal_row

st.set_page_config(page_title="Investment Memo | VC Playbook", page_icon="📗", layout="wide")
apply_theme()
sidebar()

page_header("Investment Memo", "One click turns a screened startup into a structured investment memo.", "Reports")

DATA_PATH = os.path.join(PROJECT_ROOT, "data", "startups.csv")
df = pd.read_csv(DATA_PATH)

active_row = get_active_deal_row()
active_parsed = get_active_deal_parsed()

section_title("Memo Setup", "Choose a screened company and generate a committee-ready memo draft.")

use_active = False
if active_row:
    use_active = st.checkbox(f"Use active deal — {active_row['company']}", value=True)

if use_active and active_row:
    row = active_row
    parsed = active_parsed
else:
    company = st.selectbox("Select a company", df["company"])
    row = df[df["company"] == company].iloc[0].to_dict()
    parsed = None


def build_risk_bullets(row: dict, ltv_cac: float) -> list:
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
    return risks


def build_next_steps(result, risk_bullets: list) -> list:
    if result.recommendation == "Proceed":
        steps = ["Schedule a partner meeting and align on a term sheet timeline."]
    elif result.recommendation == "Watch":
        steps = ["Request updated financials next quarter and re-screen before committing."]
    else:
        steps = ["Pass for now; revisit only if unit economics or growth improve materially."]
    steps.append("Validate revenue, CAC, and LTV figures directly against the data room.")
    steps.append("Run reference calls with 2-3 existing customers.")
    if result.weaknesses:
        steps.append(f"Pressure-test {result.weaknesses[0].lower()} with a targeted founder follow-up.")
    return steps


if st.button("Generate Investment Memo", type="primary"):
    result = score_startup(row)
    val = comparable_multiples(row["revenue_usd_k"] / 1000, row["sector_median_arr_multiple"])
    ltv_cac = round(row["ltv_usd"] / row["cac_usd"], 2) if row["cac_usd"] else 0

    narrative_sections = [
        generate_executive_summary(row, parsed),
        generate_problem(row, parsed),
        generate_solution(row, parsed),
        generate_business_model(row, parsed),
        generate_market(row, parsed),
        generate_competition(row, parsed),
    ]
    confidence_section = generate_confidence_score(row, parsed)
    risk_bullets = build_risk_bullets(row, ltv_cac)
    next_steps = build_next_steps(result, risk_bullets)

    section_title(f"Investment Memo - {row['company']}", f"{row['sector']} · {row['stage']} · Prepared by VC Playbook")
    recommendation_banner(result.recommendation, result.total)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("VC Score", f"{result.total}/100", "Weighted diligence score.", "gauge")
    with c2:
        metric_card("Recommendation", result.recommendation, "Investment committee posture.", "target")
    with c3:
        metric_card("LTV:CAC", f"{ltv_cac}x", "Unit economics signal.", "activity")
    with c4:
        metric_card("Adjusted Valuation", f"${val['adjusted_valuation']}M", "Comparable ARR multiple after discount.", "circle-dollar")

    for i, section in enumerate(narrative_sections):
        render_due_diligence_section(section, expanded=i == 0)

    with st.expander("Risks & Red Flags", expanded=False):
        text_card("Risks & Red Flags", "<br>".join(risk_bullets), "Diligence Flags")

    render_due_diligence_section(confidence_section)

    section_title("Financial Snapshot", "Key operating metrics behind the scorecard.")
    f1, f2, f3, f4, f5 = st.columns(5)
    with f1:
        metric_card("Revenue (ARR)", f"${row['revenue_usd_k']:.0f}k", "Current annualized revenue.", "circle-dollar")
    with f2:
        metric_card("MoM Growth", f"{row['mom_growth_pct']:.1f}%", "Month-over-month revenue growth.", "line-chart")
    with f3:
        metric_card("Monthly Burn", f"${row['monthly_burn_usd_k']:.0f}k", "Net cash burn per month.", "activity")
    with f4:
        metric_card("Runway", f"{row['runway_months']:.0f} mo", "Months of cash remaining.", "gauge")
    with f5:
        metric_card("Team Size", f"{row['team_size']}", "Full-time headcount.", "users")

    section_title("Valuation Summary", "Comparable ARR-multiple valuation, before and after illiquidity discount.")
    v1, v2 = st.columns(2)
    with v1:
        metric_card("Raw ARR-Multiple Valuation", f"${val['raw_valuation']}M", "Revenue multiple before discount.", "bar-chart")
    with v2:
        metric_card("Illiquidity-Adjusted Valuation", f"${val['adjusted_valuation']}M", "Early-stage adjusted estimate.", "circle-dollar")

    section_title("Next Steps", "Recommended follow-up actions before an investment committee vote.")
    text_card("Diligence Roadmap", "<br>".join(f"{i + 1}. {s}" for i, s in enumerate(next_steps)), "Action Items")

    pdf_bytes = build_memo_pdf(row, result, val, narrative_sections, risk_bullets, confidence_section, next_steps)
    st.download_button(
        "Download Investment Memo (PDF)",
        data=pdf_bytes,
        file_name=f"{row['company']}_Investment_Memo.pdf",
        mime="application/pdf",
        type="primary",
    )
    st.toast("Investment memo generated", icon="📄")
else:
    text_card(
        "Memo Studio",
        "Select a company and generate a memo to view thesis, risks, valuation range, recommendation, and a downloadable PDF.",
        "Ready",
    )
