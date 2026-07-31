import io
import os

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

from _paths import PROJECT_ROOT  # also puts the repo root on sys.path
from components.cards import metric_card, text_card, workflow_step
from components.navigation import nav_link, sidebar
from components.theme import apply_theme, page_header, section_title
from models.scoring import score_startup
from services.screening_input import (
    COMPETITION_OPTIONS,
    DEFAULT_COMPANY,
    DEFAULT_SCREENING,
    SCREENING_BOUNDS,
    SCREENING_COLUMNS,
    STAGES,
    coerce_screening,
    to_company_payload,
)
from state import get_active_deal_row, set_active_deal

st.set_page_config(page_title="Startup Screening | VC Playbook", page_icon="📗", layout="wide")
apply_theme()
sidebar()

page_header("Startup Screening", "Score a startup with the VC scorecard — from the sample dataset, your own inputs, or a CSV upload.", "Analysis")


def notify_usage(event: str) -> None:
    """Ping Formspree so the site owner knows someone ran an analysis.
    No-op unless FORMSPREE_URL is set in Streamlit secrets."""
    url = st.secrets.get("FORMSPREE_URL", "")
    if not url or st.session_state.get("usage_notified"):
        return
    try:
        requests.post(url, data={"event": event}, timeout=3)
        st.session_state["usage_notified"] = True
    except Exception:
        pass


GLOSSARY = {
    "ARR (Annual Recurring Revenue)": "The yearly value of a company's subscription revenue. A $50k/month subscription business has $600k ARR.",
    "MoM Growth": "Month-over-month revenue growth. 10% MoM means revenue grows 10% each month — roughly 3x in a year.",
    "CAC (Customer Acquisition Cost)": "How much it costs (marketing + sales) to win one new customer.",
    "LTV (Lifetime Value)": "The total revenue one customer generates before they churn. Healthy startups aim for LTV at least 3x CAC.",
    "Burn / Runway": "Burn is the cash a startup loses each month; runway is how many months of cash remain before it must raise again.",
    "Pre-money / Post-money": "Company value before an investment vs. after it. Post-money = pre-money + amount invested.",
    "Dilution": "How the founders' ownership percentage shrinks each time new shares are issued to investors.",
    "MOIC (Multiple on Invested Capital)": "How many times an investment pays back — invest $1M, return $4M, MOIC is 4x.",
    "IRR (Internal Rate of Return)": "The annualized return of an investment, accounting for how long the money was held.",
    "VC Score": "This simulator's 0-100 weighted score across unit economics, growth, market, team, and burn efficiency.",
}


with st.expander("📖 New to these terms? Open the beginner glossary"):
    g1, g2 = st.columns(2)
    terms = list(GLOSSARY.items())
    for col, chunk in ((g1, terms[:5]), (g2, terms[5:])):
        with col:
            for term, definition in chunk:
                st.markdown(f"**{term}**  \n{definition}")

section_title("How It Works", "Four steps from raw numbers to a committee-ready memo.")
h1, h2, h3, h4 = st.columns(4)
steps = [
    ("Pick a company", "Choose from the sample dataset, type details manually, or upload a CSV.", "search"),
    ("Review the profile", "Check and edit the company info and screening assumptions below.", "file-text"),
    ("Read the scorecard", "Get a 0-100 VC Score with strengths, weaknesses, and a Proceed / Watch / Pass call.", "gauge"),
    ("Continue the flow", "Carry the deal into Valuation, Cap Table, and the Investment Memo.", "clipboard"),
]
for i, (col, (title, desc, icon_name)) in enumerate(zip((h1, h2, h3, h4), steps, strict=False), start=1):
    with col:
        workflow_step(i, title, desc, icon_name)

DATA_PATH = os.path.join(PROJECT_ROOT, "data", "startups.csv")
df = pd.read_csv(DATA_PATH)

SECTORS = sorted(df["sector"].dropna().unique().tolist())
if "SaaS" not in SECTORS:
    SECTORS.append("SaaS")
if "AI" not in SECTORS:
    SECTORS.append("AI")


def csv_template() -> bytes:
    example = DEFAULT_COMPANY | DEFAULT_SCREENING | {"company": "Example Startup"}
    return pd.DataFrame([{col: example.get(col, "") for col in SCREENING_COLUMNS}]).to_csv(index=False).encode()


def selectbox_index(options: list, value: str) -> int:
    return options.index(value) if value in options else 0


def render_company_form(company_defaults: dict, screening: dict, expand_assumptions: bool = False) -> dict:
    c1, c2, c3 = st.columns(3)
    with c1:
        company = st.text_input("Company Name", company_defaults["company"])
        sector = st.selectbox("Sector", SECTORS, index=selectbox_index(SECTORS, company_defaults["sector"]))
        stage = st.selectbox("Stage", STAGES, index=selectbox_index(STAGES, company_defaults["stage"]))
        business_model = st.text_input("Business Model", company_defaults["business_model"])
    with c2:
        customers = st.text_input("Target Customers", company_defaults["customers"])
        location = st.text_input("HQ", company_defaults["location"])
        website = st.text_input("Website", company_defaults["website"])
        founding_year = st.text_input("Founding Year", company_defaults["founding_year"])
    with c3:
        revenue_model = st.text_input("Revenue Model", company_defaults["revenue_model"])
        team_size = st.number_input("Team Size", *SCREENING_BOUNDS["team_size"], int(screening["team_size"]))
        description = st.text_area("Description", company_defaults["description"], height=126)

    with st.expander("Adjust Screening Assumptions", expanded=expand_assumptions):
        s1, s2, s3 = st.columns(3)
        with s1:
            revenue_usd_k = st.number_input("Revenue ($'000 ARR)", *SCREENING_BOUNDS["revenue_usd_k"], float(screening["revenue_usd_k"]))
            mom_growth_pct = st.number_input("MoM Growth (%)", *SCREENING_BOUNDS["mom_growth_pct"], float(screening["mom_growth_pct"]))
            cac_usd = st.number_input("CAC ($)", *SCREENING_BOUNDS["cac_usd"], float(screening["cac_usd"]))
        with s2:
            ltv_usd = st.number_input("LTV ($)", *SCREENING_BOUNDS["ltv_usd"], float(screening["ltv_usd"]))
            monthly_burn_usd_k = st.number_input("Monthly Burn ($'000)", *SCREENING_BOUNDS["monthly_burn_usd_k"], float(screening["monthly_burn_usd_k"]))
            runway_months = st.number_input("Runway (months)", *SCREENING_BOUNDS["runway_months"], float(screening["runway_months"]))
        with s3:
            competition = st.selectbox(
                "Competition",
                COMPETITION_OPTIONS,
                index=selectbox_index(COMPETITION_OPTIONS, screening["competition"]),
            )
            founder_experience_score = st.slider(
                "Founder Experience (1-10)",
                *SCREENING_BOUNDS["founder_experience_score"],
                int(screening["founder_experience_score"]),
            )
            sector_median_arr_multiple = st.number_input(
                "Sector Median ARR Multiple",
                *SCREENING_BOUNDS["sector_median_arr_multiple"],
                float(screening["sector_median_arr_multiple"]),
            )

    return {
        "company": company,
        "sector": sector,
        "stage": stage,
        "business_model": business_model,
        "customers": customers,
        "location": location,
        "website": website,
        "founding_year": founding_year,
        "revenue_model": revenue_model,
        "description": description,
        "revenue_usd_k": revenue_usd_k,
        "mom_growth_pct": mom_growth_pct,
        "cac_usd": cac_usd,
        "ltv_usd": ltv_usd,
        "monthly_burn_usd_k": monthly_burn_usd_k,
        "runway_months": runway_months,
        "competition": competition,
        "founder_experience_score": founder_experience_score,
        "team_size": team_size,
        "sector_median_arr_multiple": sector_median_arr_multiple,
    }


prefill_company = st.session_state.pop("prefill_company", None)
if prefill_company:
    st.info(f"Analyzing **{prefill_company}** from the news — enter what you know about it below. Public numbers are often in the funding article itself.")

section_title("Choose Startup Source", "Start from the sample dataset, enter details manually, or upload your own CSV.")
source = st.radio(
    "Startup source",
    ["Existing Dataset", "Manual Entry", "Upload CSV"],
    horizontal=True,
    index=1 if prefill_company else 0,
)

if source == "Existing Dataset":
    company = st.selectbox("Company", df["company"])
    dataset_row = df[df["company"] == company].iloc[0].to_dict()
    company_defaults = to_company_payload(dataset_row)
    screening, _ = coerce_screening(dataset_row)
elif source == "Manual Entry":
    company_defaults = DEFAULT_COMPANY.copy()
    if prefill_company:
        company_defaults["company"] = prefill_company
    screening = DEFAULT_SCREENING.copy()
else:
    st.download_button(
        "Download CSV template",
        data=csv_template(),
        file_name="vc_playbook_template.csv",
        mime="text/csv",
        help="Fill one row per company using exactly these columns, then upload it below.",
    )
    uploaded = st.file_uploader("Upload your startup CSV", type="csv")
    company_defaults = DEFAULT_COMPANY.copy()
    screening = DEFAULT_SCREENING.copy()
    if uploaded:
        try:
            user_df = pd.read_csv(io.BytesIO(uploaded.getvalue()))
            missing = [c for c in DEFAULT_SCREENING if c not in user_df.columns]
            if missing:
                st.error(f"Your CSV is missing required columns: {', '.join(missing)}. Download the template above for the exact format.")
            else:
                pick = st.selectbox("Company from your CSV", user_df["company"]) if "company" in user_df.columns and len(user_df) > 1 else None
                user_row = (user_df[user_df["company"] == pick].iloc[0] if pick else user_df.iloc[0]).to_dict()
                company_defaults = to_company_payload(user_row)
                screening, notes = coerce_screening(user_row)
                st.success(f"Loaded {company_defaults['company']} from your CSV.")
                if notes:
                    st.warning(
                        "Some values needed adjusting before they could be scored:\n\n"
                        + "\n".join(f"- {note}" for note in notes)
                    )
        except Exception as exc:
            st.error(f"Could not read that CSV: {exc}")

section_title("Company Information", "Review and edit the company profile before running the scorecard.")
row = render_company_form(company_defaults, screening, expand_assumptions=source != "Existing Dataset")

section_title("Scorecard Result", "The score_startup engine runs unchanged on the intake profile.")
result = score_startup(row)

c1, c2, c3 = st.columns(3)
with c1:
    metric_card("VC Score", f"{result.total}/100", "Weighted diligence score for this opportunity.", "gauge")
with c2:
    metric_card("Recommendation", result.recommendation, "Proceed, Watch, or Pass based on the scorecard.", "target")
with c3:
    ltv_cac = round(row["ltv_usd"] / row["cac_usd"], 2) if row["cac_usd"] else 0
    metric_card("LTV:CAC", f"{ltv_cac}x", "Unit economics signal used by the scorecard.", "activity")

section_title("Continue the Workflow", "Carry this company into valuation, cap table, and memo without re-entering data.")
if st.button("Use This Deal →", type="primary"):
    set_active_deal(row)
    notify_usage(f"Screening run: {row['company']} ({row['sector']}, {row['stage']})")
    st.toast(f"Active deal set: {row['company']}", icon="🎯")

active_row = get_active_deal_row()
if active_row and active_row.get("company") == row.get("company"):
    n1, n2, n3 = st.columns(3)
    nav_link("pages/2_Valuation.py", label="Continue to Valuation", icon=":material/attach_money:", use_container_width=True, container=n1)
    nav_link("pages/3_Cap_Table_Returns.py", label="Continue to Cap Table", icon=":material/account_tree:", use_container_width=True, container=n2)
    nav_link("pages/4_Investment_Memo.py", label="Generate Memo", icon=":material/description:", use_container_width=True, container=n3)

left, right = st.columns([1, 1.8])
with left:
    text_card("Strengths", "<br>".join(result.strengths or ["None flagged"]), "Scorecard")
    text_card("Weaknesses", "<br>".join(result.weaknesses or ["None flagged"]), "Diligence Flags")

with right:
    values = list(result.breakdown.values())
    labels = ["Unit Econ.", "Growth", "Market", "Team", "Efficiency"]

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values + [values[0]],
            theta=labels + [labels[0]],
            fill="toself",
            name=row.get("company", "Startup"),
            line=dict(color="#141B2E", width=2),
            fillcolor="rgba(169, 121, 44, 0.30)",
            hovertemplate="%{theta}: %{r:.0f}/100<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(text="VC Scorecard Breakdown", font=dict(size=15, color="#14171F"), x=0),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(color="#14171F"),
        polar=dict(
            bgcolor="#F1EFE9",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#DEDAD0"),
            angularaxis=dict(gridcolor="#DEDAD0"),
        ),
        showlegend=False,
        margin=dict(t=48, b=20, l=40, r=40),
    )
    st.plotly_chart(fig, use_container_width=True)

section_title("Full Portfolio", "All screened companies ranked by VC score.")
df_scored = df.assign(vc_score=df.apply(lambda r: score_startup(r.to_dict()).total, axis=1))
display_columns = {
    "company": "Company", "sector": "Sector", "stage": "Stage",
    "revenue_usd_k": "Revenue ($k)", "mom_growth_pct": "Growth (% MoM)",
    "monthly_burn_usd_k": "Burn ($k/mo)", "runway_months": "Runway (mo)",
    "competition": "Competition", "team_size": "Team", "vc_score": "VC Score",
}
st.dataframe(
    df_scored[list(display_columns)]
    .sort_values("vc_score", ascending=False)
    .rename(columns=display_columns)
    .round(1),
    use_container_width=True,
    hide_index=True,
)
