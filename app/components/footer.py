import streamlit as st

from .theme import GITHUB_URL, LINKEDIN_URL, SUBSTACK_URL


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
    c1, c2, c3 = st.columns(3)
    c1.link_button("LinkedIn", LINKEDIN_URL, use_container_width=True)
    c2.link_button("GitHub", GITHUB_URL, use_container_width=True)
    c3.link_button("Substack", SUBSTACK_URL, use_container_width=True)
