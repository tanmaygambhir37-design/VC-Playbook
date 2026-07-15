import os
import sys

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(APP_DIR)
sys.path.append(APP_DIR)
sys.path.append(PROJECT_ROOT)
from components.cards import deal_banner, metric_card, text_card
from components.navigation import sidebar
from components.theme import apply_theme, page_header, section_title
from models.cap_table import simulate_rounds
from models.returns import exit_proceeds, irr_from_moic, moic, sensitivity_grid
from models.scoring import score_startup
from state import get_active_deal_row

st.set_page_config(page_title="Cap Table & Returns | VC Playbook", page_icon="📗", layout="wide")
apply_theme()
sidebar()

page_header("Cap Table & Returns", "Model ownership dilution across priced rounds, then translate it into fund-level MOIC and IRR.", "Models")

active_deal = get_active_deal_row()
if active_deal:
    deal_score = score_startup(active_deal)
    deal_banner(active_deal["company"], active_deal["sector"], active_deal["stage"], deal_score.total, deal_score.recommendation)

tab1, tab2 = st.tabs(["Cap Table", "Portfolio Returns"])

with tab1:
    section_title("Starting Position", "Set the founder ownership and implied initial ESOP pool.")
    c1, c2 = st.columns(2)
    founder_pct = c1.slider("Founders Ownership (%)", 50.0, 100.0, 90.0)
    esop_pct = 100 - founder_pct
    with c2:
        metric_card("Initial ESOP Pool", f"{esop_pct:.1f}%", "Remainder after founder ownership.", "users")

    section_title("Financing Rounds", "Configure each priced round and ESOP top-up.")
    round_defs = [
        ("Seed", 3.0, 1.0, 5.0),
        ("Series A", 12.0, 4.0, 3.0),
        ("Series B", 40.0, 12.0, 2.0),
    ]

    rounds = []
    cols = st.columns(3)
    for col, (name, default_pre, default_inv, default_esop) in zip(cols, round_defs):
        with col:
            st.markdown(f"### {name}")
            include = st.checkbox(f"Include {name}", value=True, key=f"inc_{name}")
            if include:
                pre = st.number_input(f"{name} Pre-Money ($M)", 0.5, 500.0, default_pre, key=f"pre_{name}")
                inv = st.number_input(f"{name} Investment ($M)", 0.1, 200.0, default_inv, key=f"inv_{name}")
                topup = st.slider(f"{name} ESOP Top-up (%)", 0.0, 15.0, default_esop, key=f"top_{name}")
                rounds.append({"name": name, "pre_money_usd_m": pre, "investment_usd_m": inv, "esop_topup_pct": topup})

    snapshots = simulate_rounds(founder_pct, esop_pct, rounds)

    section_title("Ownership Evolution", "Stacked ownership by holder across the funding path.")
    all_holders = sorted({h for snap in snapshots for h in snap["cap_table"]})
    chart_rows = []
    for snap in snapshots:
        for holder in all_holders:
            chart_rows.append(
                {
                    "Round": snap["round"],
                    "Holder": holder,
                    "Ownership %": snap["cap_table"].get(holder, 0),
                }
            )
    chart_df = pd.DataFrame(chart_rows)
    round_order = [s["round"] for s in snapshots]
    chart_df["Round"] = pd.Categorical(chart_df["Round"], categories=round_order, ordered=True)

    cap_table_fig = px.bar(chart_df, x="Round", y="Ownership %", color="Holder", barmode="stack")
    cap_table_fig.update_layout(
        paper_bgcolor="#0B0F17",
        plot_bgcolor="#0B0F17",
        font=dict(color="#F8FAFC"),
        xaxis=dict(gridcolor="#1F2937"),
        yaxis=dict(gridcolor="#1F2937"),
        legend=dict(bgcolor="#0B0F17"),
        margin=dict(t=20, b=20),
    )
    st.plotly_chart(cap_table_fig, use_container_width=True)

    section_title("Cap Table by Round", "Detailed holder ownership after each financing event.")
    for snap in snapshots:
        with st.expander(f"{snap['round']}" + (f" - Post-Money ${snap.get('post_money_usd_m', 0):.1f}M" if "post_money_usd_m" in snap else "")):
            table = pd.DataFrame(
                [{"Holder": h, "Ownership %": round(v, 2)} for h, v in snap["cap_table"].items()]
            ).sort_values("Ownership %", ascending=False)
            st.dataframe(table, use_container_width=True, hide_index=True)

with tab2:
    section_title("Investment Assumptions", "Set the ownership, exit, and hold-period drivers.")
    r1, r2, r3, r4 = st.columns(4)
    invested = r1.number_input("Amount Invested ($M)", 0.1, 50.0, 2.0, step=0.1)
    ownership = r2.slider("Ownership at Exit (%)", 0.5, 40.0, 8.0)
    exit_val = r3.slider("Exit Valuation ($M)", 5, 3000, 250, step=5)
    holding_period = r4.slider("Holding Period (years)", 1, 12, 6)

    proceeds = exit_proceeds(exit_val, ownership)
    m = moic(proceeds, invested)
    irr = irr_from_moic(m, holding_period)

    m1, m2, m3 = st.columns(3)
    with m1:
        metric_card("Exit Proceeds", f"${proceeds}M", "Ownership percentage multiplied by exit value.", "circle-dollar")
    with m2:
        metric_card("MOIC", f"{m}x", "Multiple on invested capital.", "bar-chart")
    with m3:
        metric_card("IRR", f"{irr}%", "Annualized return over the holding period.", "line-chart")

    section_title("Sensitivity", "IRR by exit valuation and holding period.")
    exit_range = list(range(50, 1050, 100))
    hold_range = [3, 4, 5, 6, 7, 8, 10]
    grid = sensitivity_grid(invested, ownership, exit_range, hold_range)

    returns_fig = go.Figure(
        data=go.Heatmap(
            z=grid,
            x=[f"{h}y" for h in hold_range],
            y=[f"${e}M" for e in exit_range],
            colorscale=[[0, "#EF4444"], [0.5, "#F59E0B"], [1, "#10B981"]],
            colorbar=dict(title="IRR %"),
            text=np.round(grid, 0),
            texttemplate="%{text}%",
        )
    )
    returns_fig.update_layout(
        xaxis_title="Holding Period",
        yaxis_title="Exit Valuation",
        paper_bgcolor="#0B0F17",
        plot_bgcolor="#0B0F17",
        font=dict(color="#F8FAFC"),
        xaxis=dict(gridcolor="#1F2937"),
        yaxis=dict(gridcolor="#1F2937"),
        margin=dict(t=20, b=20),
    )
    st.plotly_chart(returns_fig, use_container_width=True)

    text_card(
        "LP Lens",
        "Read this like a fund LP would: stronger cells show which combinations of exit outcome and hold period clear a fund's target IRR hurdle.",
        "Interpretation",
    )
