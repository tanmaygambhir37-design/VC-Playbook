import os
import sys

import numpy as np
import plotly.graph_objects as go
import streamlit as st

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(APP_DIR)
sys.path.append(APP_DIR)
sys.path.append(PROJECT_ROOT)
from components.cards import metric_card, text_card
from components.navigation import sidebar
from components.theme import apply_theme, page_header, section_title
from models.returns import exit_proceeds, irr_from_moic, moic, sensitivity_grid

st.set_page_config(page_title="Portfolio Returns | VC-Lab", page_icon="🚀", layout="wide")
apply_theme()
sidebar()

page_header("Portfolio Returns", "MOIC, IRR, and exit sensitivity for a single investment position.", "Models")

section_title("Investment Assumptions", "Set the ownership, exit, and hold-period drivers.")
c1, c2, c3, c4 = st.columns(4)
invested = c1.number_input("Amount Invested ($M)", 0.1, 50.0, 2.0, step=0.1)
ownership = c2.slider("Ownership at Exit (%)", 0.5, 40.0, 8.0)
exit_val = c3.slider("Exit Valuation ($M)", 5, 3000, 250, step=5)
holding_period = c4.slider("Holding Period (years)", 1, 12, 6)

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

fig = go.Figure(
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
fig.update_layout(
    xaxis_title="Holding Period",
    yaxis_title="Exit Valuation",
    paper_bgcolor="#0B0F17",
    plot_bgcolor="#0B0F17",
    font=dict(color="#F8FAFC"),
    xaxis=dict(gridcolor="#1F2937"),
    yaxis=dict(gridcolor="#1F2937"),
)
st.plotly_chart(fig, use_container_width=True)

text_card(
    "LP Lens",
    "Read this like a fund LP would: stronger cells show which combinations of exit outcome and hold period clear a fund's target IRR hurdle.",
    "Interpretation",
)
