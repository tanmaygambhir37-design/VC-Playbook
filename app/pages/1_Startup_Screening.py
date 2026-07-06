import os
import sys

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(APP_DIR)
sys.path.append(APP_DIR)
sys.path.append(PROJECT_ROOT)
from components.cards import metric_card, pill, text_card
from components.navigation import sidebar
from components.theme import apply_theme, page_header, section_title
from models.scoring import score_startup
from services.startup_parser import parse_startup

st.set_page_config(page_title="Startup Screening | VC-Lab", page_icon="🚀", layout="wide")
apply_theme()
sidebar()

page_header("Startup Screening", "AI-assisted startup intake with the existing VC scorecard engine.", "Analysis")

DATA_PATH = os.path.join(PROJECT_ROOT, "data", "startups.csv")
df = pd.read_csv(DATA_PATH)

DEFAULT_COMPANY = {
    "company": "New Startup",
    "sector": "SaaS",
    "stage": "Seed",
    "business_model": "Subscription software platform",
    "customers": "Mid-market companies",
    "location": "San Francisco, CA",
    "website": "",
    "founding_year": "2023",
    "revenue_model": "Monthly subscription",
    "description": "Early-stage company building a focused software product for a defined customer segment.",
}

DEFAULT_SCREENING = {
    "revenue_usd_k": 20.0,
    "mom_growth_pct": 10.0,
    "cac_usd": 150.0,
    "ltv_usd": 450.0,
    "monthly_burn_usd_k": 60.0,
    "runway_months": 12.0,
    "competition": "Medium",
    "founder_experience_score": 6,
    "team_size": 15,
    "sector_median_arr_multiple": 8.0,
}

SECTORS = sorted(df["sector"].dropna().unique().tolist())
if "SaaS" not in SECTORS:
    SECTORS.append("SaaS")
if "AI" not in SECTORS:
    SECTORS.append("AI")
STAGES = ["Pre-Seed", "Seed", "Series A", "Growth"]


def to_company_payload(row: dict) -> dict:
    return {
        "company": row.get("company", DEFAULT_COMPANY["company"]),
        "sector": row.get("sector", DEFAULT_COMPANY["sector"]),
        "stage": row.get("stage", DEFAULT_COMPANY["stage"]),
        "business_model": row.get("business_model", DEFAULT_COMPANY["business_model"]),
        "customers": row.get("customers", DEFAULT_COMPANY["customers"]),
        "location": row.get("location", DEFAULT_COMPANY["location"]),
        "website": row.get("website", DEFAULT_COMPANY["website"]),
        "founding_year": str(row.get("founding_year", DEFAULT_COMPANY["founding_year"])),
        "revenue_model": row.get("revenue_model", DEFAULT_COMPANY["revenue_model"]),
        "description": row.get("description", DEFAULT_COMPANY["description"]),
    }


def parsed_to_company_payload(parsed: dict) -> dict:
    return {
        "company": parsed.get("name") or DEFAULT_COMPANY["company"],
        "sector": parsed.get("sector") or DEFAULT_COMPANY["sector"],
        "stage": parsed.get("stage") or DEFAULT_COMPANY["stage"],
        "business_model": parsed.get("business_model") or DEFAULT_COMPANY["business_model"],
        "customers": parsed.get("customers") or DEFAULT_COMPANY["customers"],
        "location": parsed.get("location") or DEFAULT_COMPANY["location"],
        "website": parsed.get("website") or DEFAULT_COMPANY["website"],
        "founding_year": str(parsed.get("founding_year") or DEFAULT_COMPANY["founding_year"]),
        "revenue_model": parsed.get("revenue_model") or DEFAULT_COMPANY["revenue_model"],
        "description": parsed.get("description") or DEFAULT_COMPANY["description"],
    }


def screening_defaults(source: str, parsed: dict | None = None) -> dict:
    defaults = DEFAULT_SCREENING.copy()
    if parsed:
        defaults["team_size"] = int(parsed.get("team_size") or defaults["team_size"])
        if parsed.get("sector") == "Fintech":
            defaults.update(
                {
                    "revenue_usd_k": 900.0,
                    "mom_growth_pct": 14.0,
                    "cac_usd": 420.0,
                    "ltv_usd": 2400.0,
                    "monthly_burn_usd_k": 520.0,
                    "runway_months": 24.0,
                    "competition": "High",
                    "founder_experience_score": 9,
                    "sector_median_arr_multiple": 9.0,
                }
            )
        elif parsed.get("sector") == "AI":
            defaults.update(
                {
                    "revenue_usd_k": 850.0,
                    "mom_growth_pct": 18.0,
                    "cac_usd": 360.0,
                    "ltv_usd": 3000.0,
                    "monthly_burn_usd_k": 700.0,
                    "runway_months": 20.0,
                    "competition": "High",
                    "founder_experience_score": 9,
                    "sector_median_arr_multiple": 12.0,
                }
            )
    if source == "Existing Dataset":
        defaults["sector_median_arr_multiple"] = 8.0
    return defaults


def selectbox_index(options: list, value: str) -> int:
    return options.index(value) if value in options else 0


def render_company_form(company_defaults: dict, screening: dict) -> dict:
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
        team_size = st.number_input("Team Size", 1, 20000, int(screening["team_size"]))
        description = st.text_area("Description", company_defaults["description"], height=126)

    st.markdown('<div class="vcl-card-kicker">Screening Assumptions</div>', unsafe_allow_html=True)
    s1, s2, s3 = st.columns(3)
    with s1:
        revenue_usd_k = st.number_input("Revenue ($'000 ARR)", 0.0, 1000.0, float(screening["revenue_usd_k"]))
        mom_growth_pct = st.number_input("MoM Growth (%)", 0.0, 100.0, float(screening["mom_growth_pct"]))
        cac_usd = st.number_input("CAC ($)", 1.0, 5000.0, float(screening["cac_usd"]))
    with s2:
        ltv_usd = st.number_input("LTV ($)", 1.0, 20000.0, float(screening["ltv_usd"]))
        monthly_burn_usd_k = st.number_input("Monthly Burn ($'000)", 1.0, 1000.0, float(screening["monthly_burn_usd_k"]))
        runway_months = st.number_input("Runway (months)", 0.0, 48.0, float(screening["runway_months"]))
    with s3:
        competition = st.selectbox(
            "Competition",
            ["Low", "Medium", "High"],
            index=selectbox_index(["Low", "Medium", "High"], screening["competition"]),
        )
        founder_experience_score = st.slider(
            "Founder Experience (1-10)",
            1,
            10,
            int(screening["founder_experience_score"]),
        )
        sector_median_arr_multiple = st.number_input(
            "Sector Median ARR Multiple",
            1.0,
            50.0,
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


def render_ai_summary(parsed: dict | None, row: dict) -> None:
    if parsed:
        strengths = "".join(pill(item) for item in parsed.get("strengths", []))
        risks = "".join(pill(item) for item in parsed.get("risks", []))
        summary = parsed.get("summary") or row.get("description", "")
        business_model = parsed.get("business_model") or row.get("business_model", "")
    else:
        strengths = pill("Editable intake profile")
        risks = pill("Requires diligence validation")
        summary = row.get("description", "")
        business_model = row.get("business_model", "")

    st.markdown(
        f"""
        <div class="vcl-card">
            <div class="vcl-card-kicker">AI Summary</div>
            <div class="vcl-card-title">Company Summary</div>
            <div class="vcl-card-body">{summary}</div>
            <div style="height: 18px;"></div>
            <div class="vcl-card-title">Business Model</div>
            <div class="vcl-card-body">{business_model}</div>
            <div style="height: 18px;"></div>
            <div class="vcl-card-title">Key Strengths</div>
            <div>{strengths}</div>
            <div style="height: 12px;"></div>
            <div class="vcl-card-title">Potential Risks</div>
            <div>{risks}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


section_title("Choose Startup Source", "Start from the dataset, enter details manually, or analyze a startup website.")
source = st.radio(
    "Startup source",
    ["Existing Dataset", "Manual Entry", "AI Website Analysis"],
    horizontal=True,
)

parsed_startup = None

if source == "Existing Dataset":
    company = st.selectbox("Company", df["company"])
    dataset_row = df[df["company"] == company].iloc[0].to_dict()
    company_defaults = to_company_payload(dataset_row)
    screening = {key: dataset_row.get(key, value) for key, value in DEFAULT_SCREENING.items()}
elif source == "Manual Entry":
    company_defaults = DEFAULT_COMPANY.copy()
    screening = screening_defaults(source)
else:
    website_url = st.text_input("Startup Website", "https://www.stripe.com")
    if st.button("Analyze Startup", type="primary"):
        with st.spinner("Analyzing startup..."):
            st.session_state["parsed_startup"] = parse_startup(website_url)
            st.session_state["parsed_url"] = website_url

    parsed_startup = st.session_state.get("parsed_startup")
    if parsed_startup:
        company_defaults = parsed_to_company_payload(parsed_startup)
        screening = screening_defaults(source, parsed_startup)
    else:
        company_defaults = DEFAULT_COMPANY | {"website": website_url}
        screening = screening_defaults(source)

section_title("Company Information", "Review and edit the company profile before running the scorecard.")
row = render_company_form(company_defaults, screening)

section_title("AI Summary", "Parser output remains editable above and can later be replaced with OpenAI extraction.")
render_ai_summary(parsed_startup, row)

section_title("Continue to Screening", "The existing score_startup engine runs unchanged on the intake profile.")
result = score_startup(row)

c1, c2, c3 = st.columns(3)
with c1:
    metric_card("VC Score", f"{result.total}/100", "Weighted diligence score for this opportunity.", "gauge")
with c2:
    metric_card("Recommendation", result.recommendation, "Proceed, Watch, or Pass based on the scorecard.", "target")
with c3:
    ltv_cac = round(row["ltv_usd"] / row["cac_usd"], 2) if row["cac_usd"] else 0
    metric_card("LTV:CAC", f"{ltv_cac}x", "Unit economics signal used by the scorecard.", "activity")

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
            line=dict(color="#2563EB"),
        )
    )
    fig.update_layout(
        paper_bgcolor="#0B0F17",
        plot_bgcolor="#0B0F17",
        font=dict(color="#F8FAFC"),
        polar=dict(
            bgcolor="#111827",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#1F2937"),
            angularaxis=dict(gridcolor="#1F2937"),
        ),
        showlegend=False,
        margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

section_title("Full Portfolio", "All screened companies ranked by VC score.")
df_scored = df.assign(vc_score=df.apply(lambda r: score_startup(r.to_dict()).total, axis=1))
st.dataframe(
    df_scored.sort_values("vc_score", ascending=False),
    use_container_width=True,
    hide_index=True,
)
