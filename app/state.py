"""
state.py — Active Deal session state

Holds the single "active deal" a user is carrying through the
Screening -> Valuation -> Cap Table -> Memo workflow. Backed by Streamlit's
session_state, so it resets per browser session (no persistence layer, by
design — this is a demo workspace, not a multi-user product).
"""

import streamlit as st

_KEY = "active_deal"


def set_active_deal(row: dict, parsed: dict | None = None) -> None:
    st.session_state[_KEY] = {"row": dict(row), "parsed": parsed}


def get_active_deal_row() -> dict | None:
    deal = st.session_state.get(_KEY)
    return deal["row"] if deal else None


def get_active_deal_parsed() -> dict | None:
    deal = st.session_state.get(_KEY)
    return deal.get("parsed") if deal else None


def has_active_deal() -> bool:
    return _KEY in st.session_state


def deal_widget_key(suffix: str) -> str:
    """Stable per-deal widget key: sliders re-initialize with the deal's
    defaults when the active deal changes, but keep the user's edits while
    the deal stays the same (Streamlit persists widget state by key)."""
    row = get_active_deal_row()
    ident = row["company"] if row else "default"
    return f"{suffix}_{ident}"
