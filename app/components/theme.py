import streamlit as st


APP_NAME = "VC Playbook"
SUBTITLE = "Learn venture capital through real deals."
TAGLINE = "Read the news. Think like an investor."

GITHUB_URL = "https://github.com/tanmaygambhir37-design/VC-Playbook"
LINKEDIN_URL = "https://www.linkedin.com/in/tanmay-g-5432ba203/"
SUBSTACK_URL = "https://substack.com/@tanmaydiary/posts"


def apply_theme() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

            :root {
                --vcl-bg: #F8F5EF;
                --vcl-card: #FFFFFF;
                --vcl-card-soft: #FDFBF7;
                --vcl-border: #E5DFD3;
                --vcl-text: #111827;
                --vcl-muted: #6B7280;
                --vcl-blue: #1E3A5F;
                --vcl-gold: #C89B3C;
                --vcl-success: #0F766E;
                --vcl-warning: #B45309;
                --vcl-danger: #B91C1C;
            }

            html, body, [class*="css"], .stApp {
                font-family: 'Inter', sans-serif;
                background: var(--vcl-bg);
                color: var(--vcl-text);
            }

            .stApp {
                background: var(--vcl-bg);
            }

            [data-testid="stSidebar"] {
                background: #111827;
                border-right: 1px solid #111827;
            }

            [data-testid="stSidebar"] * {
                color: #F8F5EF;
            }

            [data-testid="stSidebar"] div[data-testid="stPageLink"] a {
                background: transparent;
                border-color: #2A3648;
                color: #F8F5EF;
            }

            [data-testid="stSidebar"] div[data-testid="stPageLink"] a:hover {
                border-color: var(--vcl-gold);
            }

            [data-testid="stSidebar"] .vcl-logo-title {
                color: #FFFFFF;
            }

            [data-testid="stSidebar"] .vcl-logo-subtitle {
                color: #B8C0CC;
            }

            [data-testid="stSidebar"] .vcl-sidebar-label {
                color: #C89B3C;
            }

            [data-testid="stSidebar"] .vcl-brand {
                border-bottom: 1px solid #2A3648;
            }

            [data-testid="stSidebarNav"] {
                display: none;
            }

            #MainMenu {
                visibility: hidden;
            }

            footer {
                visibility: hidden;
            }

            .block-container {
                padding-top: 2.25rem;
                padding-bottom: 4rem;
                max-width: 1220px;
            }

            h1, h2, h3 {
                letter-spacing: 0;
                color: var(--vcl-text);
            }

            p, li, label, span {
                color: inherit;
            }

            div[data-testid="stMetric"] {
                background: var(--vcl-card);
                border: 1px solid var(--vcl-border);
                border-radius: 8px;
                padding: 18px 18px 16px;
                box-shadow: 0 10px 30px rgba(17, 24, 39, 0.06);
            }

            div[data-testid="stMetric"] label {
                color: var(--vcl-muted);
                font-size: 0.78rem;
                font-weight: 600;
            }

            div[data-testid="stMetricValue"] {
                color: var(--vcl-text);
                font-size: 1.65rem;
                font-weight: 750;
            }

            .stButton > button,
            .stDownloadButton > button,
            .stLinkButton > a,
            div[data-testid="stPageLink"] a {
                border-radius: 8px;
                border: 1px solid var(--vcl-border);
                background: var(--vcl-card);
                color: var(--vcl-text);
                font-weight: 650;
                transition: all 160ms ease;
            }

            .stButton > button:hover,
            .stDownloadButton > button:hover,
            .stLinkButton > a:hover,
            div[data-testid="stPageLink"] a:hover {
                border-color: var(--vcl-gold);
                color: var(--vcl-blue);
                transform: translateY(-1px);
                box-shadow: 0 10px 26px rgba(200, 155, 60, 0.22);
            }

            .stButton > button[kind="primary"] {
                background: var(--vcl-blue);
                border-color: var(--vcl-blue);
                color: #FFFFFF;
            }

            .stButton > button[kind="primary"]:hover {
                background: #16304F;
                border-color: var(--vcl-gold);
                color: #FFFFFF;
            }

            [data-baseweb="tab-list"] {
                gap: 8px;
            }

            [data-baseweb="tab"] {
                border-radius: 8px;
                border: 1px solid var(--vcl-border);
                background: var(--vcl-card-soft);
                padding: 8px 14px;
            }

            [data-baseweb="tab"][aria-selected="true"] {
                background: var(--vcl-card);
                border-color: var(--vcl-blue);
            }

            .stDataFrame, .stPlotlyChart {
                border-radius: 8px;
            }

            section[data-testid="stSidebar"] .stMarkdown p {
                margin-bottom: 0;
            }

            .vcl-brand {
                border-bottom: 1px solid var(--vcl-border);
                margin-bottom: 18px;
                padding: 8px 0 18px;
            }

            .vcl-logo {
                align-items: center;
                display: flex;
                gap: 10px;
            }

            .vcl-logo-mark {
                align-items: center;
                background: var(--vcl-blue);
                border-radius: 8px;
                color: #FFFFFF;
                display: inline-flex;
                font-size: 1rem;
                font-weight: 800;
                height: 34px;
                justify-content: center;
                width: 34px;
            }

            .vcl-logo-title {
                color: var(--vcl-text);
                font-size: 1.05rem;
                font-weight: 800;
                line-height: 1;
            }

            .vcl-logo-subtitle {
                color: var(--vcl-muted);
                font-size: 0.76rem;
                margin-top: 4px;
            }

            .vcl-page-header {
                margin-bottom: 28px;
            }

            .vcl-hero {
                background:
                    linear-gradient(100deg, rgba(17, 24, 39, 0.93) 35%, rgba(17, 24, 39, 0.62) 75%, rgba(200, 155, 60, 0.35)),
                    url('https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1800&q=70');
                background-position: center;
                background-size: cover;
                border-radius: 14px;
                margin: 14px 0 4px;
                padding: 34px 40px;
            }

            .vcl-hero .vcl-eyebrow {
                color: var(--vcl-gold);
            }

            .vcl-hero .vcl-page-title {
                color: #FFFFFF;
                font-size: clamp(2rem, 4.5vw, 3.6rem);
                margin-bottom: 8px;
            }

            .vcl-hero .vcl-subtitle {
                color: #F8F5EF;
            }

            .vcl-deal-card {
                background: var(--vcl-card);
                border: 1px solid var(--vcl-border);
                border-left: 3px solid var(--vcl-gold);
                border-radius: 8px;
                height: 100%;
                padding: 16px 18px;
            }

            .vcl-deal-amount {
                color: var(--vcl-blue);
                font-size: 1.15rem;
                font-weight: 800;
            }

            .vcl-deal-sector {
                background: rgba(200, 155, 60, 0.14);
                border: 1px solid rgba(200, 155, 60, 0.4);
                border-radius: 999px;
                color: #8A6A25;
                display: inline-block;
                font-size: 0.7rem;
                font-weight: 800;
                letter-spacing: 0.05em;
                margin-left: 8px;
                padding: 2px 10px;
                text-transform: uppercase;
                vertical-align: middle;
            }

            .vcl-deal-name {
                color: var(--vcl-text);
                font-size: 1rem;
                font-weight: 750;
                margin-bottom: 4px;
            }

            .vcl-deal-body {
                color: var(--vcl-muted);
                font-size: 0.88rem;
                line-height: 1.55;
            }

            .vcl-deal-body strong {
                color: var(--vcl-text);
            }

            .vcl-hero-inner {
                max-width: 820px;
            }

            .vcl-topbar {
                align-items: center;
                display: flex;
                gap: 10px;
                justify-content: flex-end;
                padding-top: 6px;
            }

            .vcl-topbar a {
                border: 1px solid var(--vcl-border);
                border-radius: 999px;
                color: var(--vcl-text);
                font-size: 0.82rem;
                font-weight: 650;
                padding: 7px 16px;
                text-decoration: none;
                transition: border-color 160ms ease;
            }

            .vcl-topbar a:hover {
                border-color: var(--vcl-blue);
            }

            .vcl-topbar-bio {
                color: var(--vcl-muted);
                font-size: 0.82rem;
                margin-right: auto;
            }

            .vcl-news-card {
                background: var(--vcl-card);
                border: 1px solid var(--vcl-border);
                border-radius: 8px;
                display: block;
                height: 100%;
                padding: 18px;
                text-decoration: none;
                transition: border-color 160ms ease, transform 160ms ease;
            }

            .vcl-news-card:hover {
                border-color: var(--vcl-blue);
                transform: translateY(-2px);
            }

            .vcl-news-source {
                color: var(--vcl-blue);
                font-size: 0.72rem;
                font-weight: 800;
                letter-spacing: 0.07em;
                margin-bottom: 8px;
                text-transform: uppercase;
            }

            .vcl-news-title {
                color: var(--vcl-text);
                font-size: 0.98rem;
                font-weight: 700;
                line-height: 1.4;
                margin-bottom: 8px;
            }

            .vcl-news-meta {
                color: var(--vcl-muted);
                font-size: 0.8rem;
            }

            .vcl-eyebrow {
                color: var(--vcl-blue);
                font-size: 0.78rem;
                font-weight: 750;
                letter-spacing: 0.08em;
                margin-bottom: 10px;
                text-transform: uppercase;
            }

            .vcl-page-title {
                color: var(--vcl-text);
                font-size: clamp(2.2rem, 6vw, 5.4rem);
                font-weight: 820;
                letter-spacing: 0;
                line-height: 0.95;
                margin: 0 0 16px;
            }

            .vcl-workspace-title {
                color: var(--vcl-text);
                font-size: clamp(2rem, 4vw, 3.2rem);
                font-weight: 800;
                letter-spacing: 0;
                line-height: 1.05;
                margin: 0 0 10px;
            }

            .vcl-subtitle {
                color: var(--vcl-text);
                font-size: 1.25rem;
                font-weight: 650;
                margin-bottom: 8px;
            }

            .vcl-copy {
                color: var(--vcl-muted);
                font-size: 1rem;
                line-height: 1.7;
                max-width: 760px;
            }

            .vcl-card {
                background: var(--vcl-card);
                border: 1px solid var(--vcl-border);
                border-radius: 8px;
                box-shadow: 0 10px 30px rgba(17, 24, 39, 0.06);
                height: 100%;
                padding: 22px;
                transition: border-color 160ms ease, box-shadow 160ms ease, transform 160ms ease;
            }

            .vcl-card:hover {
                border-color: var(--vcl-gold);
                box-shadow: 0 14px 38px rgba(17, 24, 39, 0.1);
                transform: translateY(-2px);
            }

            .vcl-deal-banner {
                align-items: center;
                background: var(--vcl-card-soft);
                border: 1px solid var(--vcl-border);
                border-radius: 999px;
                display: inline-flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-bottom: 26px;
                padding: 9px 18px;
            }

            .vcl-deal-tag {
                color: var(--vcl-blue);
                font-size: 0.7rem;
                font-weight: 800;
                letter-spacing: 0.07em;
                text-transform: uppercase;
            }

            .vcl-deal-company {
                color: var(--vcl-text);
                font-size: 0.88rem;
                font-weight: 750;
            }

            .vcl-deal-meta {
                color: var(--vcl-muted);
                font-size: 0.85rem;
            }

            .vcl-deal-dot {
                color: #C9C1B2;
            }

            .vcl-deal-score {
                font-size: 0.85rem;
                font-weight: 700;
            }

            .vcl-rec-banner {
                align-items: center;
                border: 1px solid;
                border-radius: 10px;
                display: flex;
                gap: 14px;
                margin-bottom: 24px;
                padding: 16px 22px;
            }

            .vcl-rec-dot {
                border-radius: 999px;
                flex-shrink: 0;
                height: 10px;
                width: 10px;
            }

            .vcl-rec-text {
                font-size: 1.08rem;
                font-weight: 820;
                letter-spacing: 0.03em;
            }

            .vcl-rec-score {
                color: var(--vcl-muted);
                font-size: 0.9rem;
                font-weight: 650;
            }

            .vcl-card-kicker {
                color: var(--vcl-muted);
                font-size: 0.76rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                margin-bottom: 12px;
                text-transform: uppercase;
            }

            .vcl-card-title {
                color: var(--vcl-text);
                font-size: 1.05rem;
                font-weight: 760;
                margin-bottom: 8px;
            }

            .vcl-card-body {
                color: var(--vcl-muted);
                font-size: 0.92rem;
                line-height: 1.55;
            }

            .vcl-icon {
                align-items: center;
                background: rgba(30, 58, 95, 0.08);
                border: 1px solid rgba(30, 58, 95, 0.25);
                border-radius: 8px;
                color: var(--vcl-blue);
                display: inline-flex;
                height: 38px;
                justify-content: center;
                margin-bottom: 16px;
                width: 38px;
            }

            .vcl-icon svg {
                height: 19px;
                stroke: currentColor;
                width: 19px;
            }

            .vcl-metric-value {
                color: var(--vcl-text);
                font-size: 2rem;
                font-weight: 820;
                line-height: 1;
                margin-bottom: 8px;
            }

            .vcl-section {
                border-top: 1px solid var(--vcl-border);
                margin-top: 42px;
                padding-top: 34px;
            }

            .vcl-section-title {
                color: var(--vcl-text);
                font-size: 1.45rem;
                font-weight: 780;
                margin-bottom: 6px;
            }

            .vcl-section-subtitle {
                color: var(--vcl-muted);
                font-size: 0.96rem;
                margin-bottom: 20px;
            }

            .vcl-workflow-step {
                min-height: 168px;
            }

            .vcl-step-number {
                color: var(--vcl-blue);
                font-size: 0.8rem;
                font-weight: 800;
                margin-bottom: 10px;
            }


            .vcl-pill {
                border: 1px solid var(--vcl-border);
                border-radius: 999px;
                color: var(--vcl-muted);
                display: inline-flex;
                font-size: 0.78rem;
                font-weight: 650;
                margin: 0 8px 8px 0;
                padding: 6px 10px;
            }

            .vcl-footer {
                border-top: 1px solid var(--vcl-border);
                color: var(--vcl-muted);
                margin-top: 46px;
                padding-top: 26px;
            }

            .vcl-footer strong {
                color: var(--vcl-text);
            }

            .vcl-sidebar-label {
                color: #8A6A25;
                font-size: 0.7rem;
                font-weight: 800;
                letter-spacing: 0.08em;
                margin: 18px 0 8px;
                text-transform: uppercase;
            }

            .vcl-muted {
                color: var(--vcl-muted);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str, eyebrow: str = APP_NAME) -> None:
    st.markdown(
        f"""
        <div class="vcl-page-header">
            <div class="vcl-eyebrow">{eyebrow}</div>
            <div class="vcl-workspace-title">{title}</div>
            <div class="vcl-copy">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def hide_sidebar() -> None:
    """Landing page: no sidebar, no collapsed-sidebar arrow, full-width hero."""
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
            [data-testid="collapsedControl"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def landing_header() -> None:
    st.markdown(
        f"""
        <div class="vcl-hero">
            <div class="vcl-hero-inner">
                <div class="vcl-eyebrow">{TAGLINE}</div>
                <div class="vcl-page-title">{APP_NAME}</div>
                <div class="vcl-subtitle">
                    Read today's funding news. Analyze any startup. Write an investment memo.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(title: str, subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div class="vcl-section">
            <div class="vcl-section-title">{title}</div>
            <div class="vcl-section-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
