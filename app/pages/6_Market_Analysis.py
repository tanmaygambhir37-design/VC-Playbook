import os
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(APP_DIR)
sys.path.append(APP_DIR)
sys.path.append(PROJECT_ROOT)
from components.cards import metric_card, text_card
from components.navigation import sidebar
from components.theme import apply_theme, page_header, section_title
from models.scoring import score_startup

st.set_page_config(page_title="Market Analysis | VC Playbook", page_icon="📗", layout="wide")
apply_theme()
sidebar()

page_header("Market Analysis", "Sector, stage, and competitive pattern views for diligence context.", "Analysis")

DATA_PATH = os.path.join(PROJECT_ROOT, "data", "startups.csv")
df = pd.read_csv(DATA_PATH)
df_scored = df.assign(vc_score=df.apply(lambda r: score_startup(r.to_dict()).total, axis=1))

section_title("Market Snapshot", "Compare opportunity quality across sectors and funding stages.")
c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_card("Sectors", f"{df_scored['sector'].nunique()}", "Unique market categories in the dataset.", "bar-chart")
with c2:
    metric_card("Stages", f"{df_scored['stage'].nunique()}", "Funding stages represented.", "target")
with c3:
    metric_card("Median ARR", f"${df_scored['revenue_usd_k'].median()/1000:.1f}M", "Median annual recurring revenue.", "circle-dollar")
with c4:
    metric_card("Median Growth", f"{df_scored['mom_growth_pct'].median():.0f}%", "Median month-over-month growth.", "line-chart")

sector_summary = (
    df_scored.groupby("sector", as_index=False)
    .agg(
        companies=("company", "count"),
        average_vc_score=("vc_score", "mean"),
        median_growth=("mom_growth_pct", "median"),
        median_arr_k=("revenue_usd_k", "median"),
    )
    .sort_values("average_vc_score", ascending=False)
)

section_title("Sector Quality", "Average VC score by market category.")
fig = px.bar(
    sector_summary,
    x="sector",
    y="average_vc_score",
    color="average_vc_score",
    color_continuous_scale=["#EF4444", "#F59E0B", "#10B981"],
)
fig.update_layout(
    paper_bgcolor="#0B0F17",
    plot_bgcolor="#0B0F17",
    font=dict(color="#F8FAFC"),
    xaxis=dict(gridcolor="#1F2937"),
    yaxis=dict(gridcolor="#1F2937", title="Average VC Score"),
    coloraxis_showscale=False,
)
st.plotly_chart(fig, use_container_width=True)

left, right = st.columns([1.35, 1])
with left:
    section_title("Sector Table", "Market-by-market operating snapshot.")
    display = sector_summary.assign(median_arr_m=sector_summary["median_arr_k"] / 1000).drop(columns=["median_arr_k"])
    st.dataframe(display, use_container_width=True, hide_index=True)

with right:
    section_title("Competitive Intensity", "Distribution of competition signals.")
    competition_counts = df_scored["competition"].value_counts().rename_axis("competition").reset_index(name="companies")
    fig2 = px.pie(competition_counts, names="competition", values="companies", hole=0.55)
    fig2.update_layout(
        paper_bgcolor="#0B0F17",
        plot_bgcolor="#0B0F17",
        font=dict(color="#F8FAFC"),
        legend=dict(bgcolor="#0B0F17"),
        margin=dict(t=10, b=10),
    )
    st.plotly_chart(fig2, use_container_width=True)

text_card(
    "Market Analysis Note",
    "This module summarizes the existing dataset for diligence orientation. It does not add or modify the underlying financial scoring, valuation, cap table, or returns formulas.",
    "Scope",
)
