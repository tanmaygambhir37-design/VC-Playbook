import os
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(APP_DIR)
sys.path.append(APP_DIR)
sys.path.append(PROJECT_ROOT)
from components.cards import metric_card
from components.navigation import sidebar
from components.theme import apply_theme, page_header, section_title
from models.cap_table import simulate_rounds

st.set_page_config(page_title="Cap Table | VC-Lab", page_icon="🚀", layout="wide")
apply_theme()
sidebar()

page_header("Cap Table", "Model founder and investor dilution across sequential priced rounds.", "Models")

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

fig = px.bar(chart_df, x="Round", y="Ownership %", color="Holder", barmode="stack")
fig.update_layout(
    paper_bgcolor="#0B0F17",
    plot_bgcolor="#0B0F17",
    font=dict(color="#F8FAFC"),
    xaxis=dict(gridcolor="#1F2937"),
    yaxis=dict(gridcolor="#1F2937"),
    legend=dict(bgcolor="#0B0F17"),
)
st.plotly_chart(fig, use_container_width=True)

section_title("Cap Table by Round", "Detailed holder ownership after each financing event.")
for snap in snapshots:
    with st.expander(f"{snap['round']}" + (f" - Post-Money ${snap.get('post_money_usd_m', 0):.1f}M" if "post_money_usd_m" in snap else "")):
        table = pd.DataFrame(
            [{"Holder": h, "Ownership %": round(v, 2)} for h, v in snap["cap_table"].items()]
        ).sort_values("Ownership %", ascending=False)
        st.dataframe(table, use_container_width=True, hide_index=True)
