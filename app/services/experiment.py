"""experiment.py — one A/B test on the landing flow.

Experiment `landing-cta-01`: does dropping the visitor straight into a
valuation (treatment B) lift the valuation-completion rate versus sending them
to the workspace dashboard first (control A)?

Assignment is deterministic from the session id (~50/50), stable for the whole
visit. The keep-awake bot is excluded so automated traffic never enters the
data. Milestones are recorded once per session as GoatCounter hits under
`/exp/<id>/<bucket>`, so counts are aggregatable and exportable for free.

Funnel (one metric): landing/<variant>  ->  valuation/<variant>
    completion rate = valuation / landing, per variant.
"""

import hashlib

import streamlit as st

from services.analytics import experiment_hit, session_id, track_event, track_source

EXPERIMENT_ID = "landing-cta-01"
_SAW_HOME = "_vcl_saw_home"


def is_excluded() -> bool:
    """True for the keep-awake bot (visits with ?keepalive=1) — never counted."""
    try:
        return str(st.query_params.get("keepalive", "")).lower() not in ("", "0", "false")
    except Exception:
        return False


def _assign(sid: str) -> str:
    """Pure, deterministic ~50/50 split from a session id (unit-testable)."""
    return "B" if int(hashlib.sha1(sid.encode()).hexdigest(), 16) % 2 else "A"


def variant() -> str:
    """Stable A/B assignment for this session (~50/50). Excluded traffic is 'A'
    but never recorded, so it can't skew either arm."""
    key = f"_vcl_variant_{EXPERIMENT_ID}"
    if key not in st.session_state:
        st.session_state[key] = _assign(session_id())
    return st.session_state[key]


def primary_cta() -> tuple[str, str]:
    """(label, target page) for the hero's primary button, by variant."""
    if variant() == "B":
        return "Value a startup in 2 minutes →", "pages/2_Valuation.py"
    return "Open the Simulator", "pages/0_Dashboard.py"


def record_landing() -> None:
    """Denominator: this session saw the landing page (non-bot).

    Also logs the acquisition channel (Round 2) — same session, same guard.
    """
    if is_excluded():
        return
    st.session_state[_SAW_HOME] = True
    experiment_hit(f"landing/{variant()}", EXPERIMENT_ID)
    track_source("landing")


def record_valuation() -> None:
    """Numerator: a home-origin session reached a computed valuation."""
    if is_excluded() or not st.session_state.get(_SAW_HOME):
        return
    experiment_hit(f"valuation/{variant()}", EXPERIMENT_ID)
    track_event("valuation_completed", once_per_session=True, variant=variant())
    track_source("valuation")
