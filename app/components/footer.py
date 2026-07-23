import streamlit as st

from .theme import GITHUB_URL, LINKEDIN_URL, PORTFOLIO_URL, RESEARCH_URL, SUBSTACK_URL


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
    cols = st.columns(5)
    cols[0].link_button("Portfolio", PORTFOLIO_URL, use_container_width=True)
    cols[1].link_button("Research", RESEARCH_URL, use_container_width=True)
    cols[2].link_button("LinkedIn", LINKEDIN_URL, use_container_width=True)
    cols[3].link_button("GitHub", GITHUB_URL, use_container_width=True)
    cols[4].link_button("Substack", SUBSTACK_URL, use_container_width=True)
