import re

import requests
import streamlit as st

from services.analytics import track_event
from .theme import (
    GITHUB_URL,
    ISSUES_URL,
    LINKEDIN_URL,
    PORTFOLIO_URL,
    RESEARCH_URL,
    SUBSTACK_SUBSCRIBE_URL,
    SUBSTACK_URL,
)

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _secret(key: str) -> str:
    try:
        return str(st.secrets.get(key, ""))
    except Exception:
        return ""


def email_capture() -> None:
    """Ask for the return visit.

    Without a signup endpoint configured this still renders — it just points at
    Substack instead of collecting the address here.
    """
    endpoint = _secret("EMAIL_SIGNUP_URL") or _secret("FORMSPREE_URL")

    st.markdown(
        """
        <div class="vcl-capture">
            <div class="vcl-card-kicker">Weekly</div>
            <div class="vcl-capture-title">One email a week: the deals worth studying, and why.</div>
            <div class="vcl-card-body">
                The same curated rounds that feed this simulator, with the reasoning attached —
                plus every new prediction as it's logged.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not endpoint:
        st.link_button("Subscribe on Substack →", SUBSTACK_SUBSCRIBE_URL, use_container_width=False)
        return

    if st.session_state.get("_subscribed"):
        st.success("You're on the list — thank you.")
        return

    with st.form("email_capture", clear_on_submit=True):
        cols = st.columns([3, 1])
        address = cols[0].text_input("Email", placeholder="you@university.edu", label_visibility="collapsed")
        submitted = cols[1].form_submit_button("Subscribe", use_container_width=True, type="primary")
    if submitted:
        if not _EMAIL_RE.match(address.strip()):
            st.error("That doesn't look like an email address.")
            return
        try:
            requests.post(endpoint, data={"email": address.strip()}, timeout=6)
        except Exception:
            st.error("Couldn't reach the signup service — try the Substack link below.")
            st.link_button("Subscribe on Substack →", SUBSTACK_SUBSCRIBE_URL)
            return
        # The address goes to the signup endpoint only. The analytics event
        # records that a signup happened and nothing about who.
        track_event("email_signup")
        st.session_state["_subscribed"] = True
        st.rerun()


def footer() -> None:
    st.markdown(
        """
        <div class="vcl-footer">
            <div><strong>Built by Tanmay Gambhir</strong></div>
            <div>Bocconi x ESSEC · Graduating 2028 · Chartered Accountant · Management Consultant</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    ask1, ask2 = st.columns(2)
    ask1.link_button("⭐ Star the repo on GitHub", GITHUB_URL, use_container_width=True)
    ask2.link_button("💬 Tell me what's missing", ISSUES_URL, use_container_width=True)

    cols = st.columns(5)
    cols[0].link_button("Portfolio", PORTFOLIO_URL, use_container_width=True)
    cols[1].link_button("Research", RESEARCH_URL, use_container_width=True)
    cols[2].link_button("LinkedIn", LINKEDIN_URL, use_container_width=True)
    cols[3].link_button("GitHub", GITHUB_URL, use_container_width=True)
    cols[4].link_button("Substack", SUBSTACK_URL, use_container_width=True)
