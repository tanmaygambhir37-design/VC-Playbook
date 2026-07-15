import streamlit as st

from .theme import APP_NAME, SUBTITLE


def nav_link(page: str, label: str, icon: str | None = None, use_container_width: bool = False, container=st) -> None:
    try:
        container.page_link(page, label=label, icon=icon, use_container_width=use_container_width)
    except KeyError:
        container.markdown(f'<span class="vcl-pill">{label}</span>', unsafe_allow_html=True)


def sidebar() -> None:
    with st.sidebar:
        st.markdown(
            f"""
            <div class="vcl-brand">
                <div class="vcl-logo">
                    <span class="vcl-logo-mark">VC</span>
                    <span>
                        <div class="vcl-logo-title">{APP_NAME}</div>
                        <div class="vcl-logo-subtitle">{SUBTITLE}</div>
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        nav_link("app.py", label="Home", icon=":material/home:")
        nav_link("pages/0_Dashboard.py", label="Dashboard", icon=":material/dashboard:")

        st.markdown('<div class="vcl-sidebar-label">News</div>', unsafe_allow_html=True)
        nav_link("pages/7_VC_Pulse.py", label="VC Pulse", icon=":material/newspaper:")

        st.markdown('<div class="vcl-sidebar-label">Analysis</div>', unsafe_allow_html=True)
        nav_link("pages/1_Startup_Screening.py", label="Startup Screening", icon=":material/troubleshoot:")
        nav_link("pages/6_Market_Analysis.py", label="Market Analysis", icon=":material/query_stats:")
        nav_link("pages/2_Valuation.py", label="Valuation", icon=":material/attach_money:")

        st.markdown('<div class="vcl-sidebar-label">Models</div>', unsafe_allow_html=True)
        nav_link("pages/3_Cap_Table_Returns.py", label="Cap Table & Returns", icon=":material/account_tree:")

        st.markdown('<div class="vcl-sidebar-label">Reports</div>', unsafe_allow_html=True)
        nav_link("pages/5_Investment_Memo.py", label="Investment Memo", icon=":material/description:")

        st.markdown('<div class="vcl-sidebar-label">Settings</div>', unsafe_allow_html=True)
        nav_link("pages/8_About_VC_Lab.py", label="About VC Playbook", icon=":material/settings:")
