"""dataset.py — the sample dataset, read once and scored once.

Four pages were each re-reading startups.csv and re-running the scorecard over
all 28 rows on every rerun, which on Streamlit means every slider drag. None of
that work depends on the widgets, so it belongs behind a cache.
"""

import os

import pandas as pd
import streamlit as st

from models.scoring import score_startup

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "startups.csv")


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


@st.cache_data
def scored_dataset() -> pd.DataFrame:
    """Sample companies with their VC score and Proceed/Watch/Pass call."""
    frame = load_data()
    results = frame.apply(lambda r: score_startup(r.to_dict()), axis=1)
    return frame.assign(
        vc_score=[r.total for r in results],
        recommendation=[r.recommendation for r in results],
    )
