import streamlit as st


APP_NAME = "VC Playbook"
SUBTITLE = "Learn venture capital through real deals."
TAGLINE = "Read the news. Think like an investor."

GITHUB_URL = "https://github.com/tanmaygambhir37-design/VC-Playbook"
LINKEDIN_URL = "https://www.linkedin.com/in/tanmay-g-5432ba203/"
SUBSTACK_URL = "https://substack.com/@tanmaydiary/posts"
SUBSTACK_SUBSCRIBE_URL = "https://tanmaydiary.substack.com/subscribe"
PORTFOLIO_URL = "https://tanmaygambhir37-design.github.io/#top"
RESEARCH_URL = "https://tanmaygambhir37-design.github.io/investment-research/"
CASE_STUDY_URL = f"{GITHUB_URL}/blob/main/reports/case-study-bending-spoons.md"
ISSUES_URL = f"{GITHUB_URL}/issues/new"


def apply_theme() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,500;0,9..144,600;0,9..144,700;1,9..144,500&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

            :root {
                --vcl-bg: #FAFAF7;
                --vcl-card: #FFFFFF;
                --vcl-card-soft: #F1EFE9;
                --vcl-border: #DEDAD0;
                --vcl-text: #14171F;
                --vcl-muted: #4B5164;
                --vcl-blue: #141B2E;
                --vcl-gold: #A9792C;
                --vcl-success: #3D6B5C;
                --vcl-warning: #B45309;
                --vcl-danger: #B91C1C;

                /* Type scale. Everything in the app picks a step from this
                   list — there is no arbitrary font-size anywhere else.
                   Before this there were twenty distinct sizes, including
                   five body sizes between 0.88 and 0.98rem that read as
                   sloppiness rather than hierarchy. */
                --fs-2xs: 0.72rem;   /* uppercase micro-labels: kickers, sources, tags */
                --fs-xs:  0.82rem;   /* meta, captions, pills, nav */
                --fs-sm:  0.92rem;   /* body copy inside cards */
                --fs-md:  1rem;      /* base copy, card headlines */
                --fs-lg:  1.12rem;   /* card titles, deal names, emphasis */
                --fs-xl:  1.28rem;   /* hero subtitle */
                --fs-2xl: 1.5rem;    /* section titles */
                --fs-3xl: 1.85rem;   /* big numbers */

                /* Box geometry: one padding value per surface size, two
                   radii, three grid heights. */
                --pad-card: 20px;
                --pad-card-tight: 16px 18px;
                --pad-surface: 30px 34px;
                --pad-pill: 7px 14px;
                --radius: 8px;
                --radius-lg: 14px;
                --card-min-sm: 112px;   /* headline cards */
                --card-min-md: 170px;   /* deal cards, workflow steps */
                --card-min-lg: 232px;   /* side-by-side proof cards */
            }

            html, body, [class*="css"], .stApp {
                font-family: 'IBM Plex Sans', sans-serif;
                background: var(--vcl-bg);
                color: var(--vcl-text);
            }

            h1, h2, h3, .vcl-page-title, .vcl-section-title, .vcl-card-title, .vcl-deal-name {
                font-family: 'Fraunces', serif !important;
            }

            .vcl-eyebrow, .vcl-card-kicker, .vcl-news-source, .vcl-sidebar-label,
            .vcl-deal-amount, .vcl-deal-sector, .vcl-metric-value, .vcl-step-number {
                font-family: 'IBM Plex Mono', monospace !important;
            }

            /* Equal card heights so grids read as aligned rows */
            .vcl-news-card { min-height: var(--card-min-sm); display: flex; flex-direction: column; }
            .vcl-news-card .vcl-news-meta { margin-top: auto; }
            .vcl-deal-card { min-height: var(--card-min-md); }

            .stApp {
                background: var(--vcl-bg);
            }

            [data-testid="stSidebar"] {
                background: #141B2E;
                border-right: 1px solid #141B2E;
            }

            [data-testid="stSidebar"] * {
                color: #FAFAF7;
            }

            [data-testid="stSidebar"] div[data-testid="stPageLink"] a {
                background: transparent;
                border-color: #2A3350;
                color: #FAFAF7;
            }

            [data-testid="stSidebar"] div[data-testid="stPageLink"] a:hover {
                border-color: var(--vcl-gold);
            }

            [data-testid="stSidebar"] .vcl-logo-title {
                color: #FFFFFF;
            }

            [data-testid="stSidebar"] .vcl-logo-subtitle {
                color: #B9BECC;
            }

            [data-testid="stSidebar"] .vcl-sidebar-label {
                color: #A9792C;
            }

            [data-testid="stSidebar"] .vcl-brand {
                border-bottom: 1px solid #2A3350;
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
                padding-top: 1.1rem;
                padding-bottom: 3rem;
                max-width: 1220px;
            }

            h1, h2, h3 {
                letter-spacing: 0;
                color: var(--vcl-text);
            }

            p, li, label, span {
                color: inherit;
            }

            /* No styling for st.metric: the app renders every number through
               metric_card() instead, and the leftover rules were a second,
               differently-sized metric look that nothing used. */

            .stButton > button,
            .stDownloadButton > button,
            .stLinkButton > a,
            div[data-testid="stPageLink"] a {
                border-radius: var(--radius);
                border: 1px solid var(--vcl-border);
                background: var(--vcl-card);
                color: var(--vcl-text);
                font-size: var(--fs-sm);
                font-weight: 650;
                transition: all 160ms ease;
            }

            /* Streamlit nests button labels four levels deep and pins them to
               14px, a hair under the card body size — enough to make every
               button read as slightly off-scale. The intermediate wrappers
               carry their own size, so this has to be set on the label itself
               and has to outrank the generated emotion class. */
            .stButton > button p,
            .stDownloadButton > button p,
            .stLinkButton > a p,
            div[data-testid="stPageLink"] a p {
                font-size: var(--fs-sm) !important;
            }

            div[data-testid="stCaptionContainer"],
            div[data-testid="stCaptionContainer"] p,
            .stCaption, .stCaption p {
                font-size: var(--fs-xs) !important;
            }

            /* Form chrome. The screening page is now the end of the funnel and
               is almost entirely widgets, so its labels, radio options and
               expander headers have to sit on the scale like everything else. */
            div[data-testid="stWidgetLabel"] p,
            div[data-testid="stWidgetLabel"] label,
            .stTextInput label p, .stNumberInput label p, .stSelectbox label p,
            .stTextArea label p, .stSlider label p, .stRadio label p,
            .stCheckbox label p, .stFileUploader label p, .stMultiSelect label p,
            [data-testid="stExpander"] summary p,
            [data-testid="stExpander"] summary {
                font-size: var(--fs-xs) !important;
            }

            .stTextInput input,
            .stNumberInput input,
            .stTextArea textarea,
            [data-testid="stSelectbox"] div[value],
            [data-baseweb="select"] > div {
                font-size: var(--fs-sm) !important;
            }

            /* Slider end-stops and the value bubble above the handle. */
            [data-testid="stSliderTickBar"] p,
            [data-testid="stSliderThumbValue"] p {
                font-size: var(--fs-2xs) !important;
            }

            .stButton > button:hover,
            .stDownloadButton > button:hover,
            .stLinkButton > a:hover,
            div[data-testid="stPageLink"] a:hover {
                border-color: var(--vcl-gold);
                color: var(--vcl-blue);
                transform: translateY(-1px);
                box-shadow: 0 10px 26px rgba(169, 121, 44, 0.22);
            }

            .stButton > button[kind="primary"] {
                background: var(--vcl-blue);
                border-color: var(--vcl-blue);
                color: #FFFFFF;
            }

            .stButton > button[kind="primary"]:hover {
                background: #0F1526;
                border-color: var(--vcl-gold);
                color: #FFFFFF;
            }

            [data-baseweb="tab-list"] {
                gap: 8px;
            }

            [data-baseweb="tab"] {
                border-radius: var(--radius);
                border: 1px solid var(--vcl-border);
                background: var(--vcl-card-soft);
                padding: 8px 14px;
            }

            [data-baseweb="tab"][aria-selected="true"] {
                background: var(--vcl-card);
                border-color: var(--vcl-blue);
            }

            .stDataFrame, .stPlotlyChart {
                border-radius: var(--radius);
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
                border-radius: var(--radius);
                color: #FFFFFF;
                display: inline-flex;
                font-size: var(--fs-md);
                font-weight: 800;
                height: 34px;
                justify-content: center;
                width: 34px;
            }

            .vcl-logo-title {
                color: var(--vcl-text);
                font-size: var(--fs-lg);
                font-weight: 800;
                line-height: 1;
            }

            .vcl-logo-subtitle {
                color: var(--vcl-muted);
                font-size: var(--fs-2xs);
                margin-top: 4px;
            }

            .vcl-page-header {
                margin-bottom: 28px;
            }

            .vcl-hero {
                background:
                    linear-gradient(100deg, rgba(17, 24, 39, 0.93) 35%, rgba(17, 24, 39, 0.62) 75%, rgba(169, 121, 44, 0.35)),
                    url('https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1800&q=70');
                background-position: center;
                background-size: cover;
                border-radius: var(--radius-lg);
                margin: 14px 0 4px;
                padding: var(--pad-surface);
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
                color: #FAFAF7;
            }

            .vcl-deal-card {
                background: var(--vcl-card);
                border: 1px solid var(--vcl-border);
                border-left: 3px solid var(--vcl-gold);
                border-radius: var(--radius);
                height: 100%;
                padding: var(--pad-card-tight);
            }

            .vcl-deal-amount {
                color: var(--vcl-blue);
                font-size: var(--fs-lg);
                font-weight: 800;
            }

            .vcl-deal-sector {
                background: rgba(169, 121, 44, 0.14);
                border: 1px solid rgba(169, 121, 44, 0.4);
                border-radius: 999px;
                color: #8A6420;
                display: inline-block;
                font-size: var(--fs-2xs);
                font-weight: 800;
                letter-spacing: 0.05em;
                margin-left: 8px;
                padding: 2px 10px;
                text-transform: uppercase;
                vertical-align: middle;
            }

            .vcl-deal-name {
                color: var(--vcl-text);
                font-size: var(--fs-md);
                font-weight: 750;
                margin-bottom: 4px;
            }

            .vcl-deal-body {
                color: var(--vcl-muted);
                font-size: var(--fs-sm);
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
                font-size: var(--fs-xs);
                font-weight: 650;
                padding: var(--pad-pill);
                text-decoration: none;
                transition: border-color 160ms ease;
            }

            .vcl-topbar a:hover {
                border-color: var(--vcl-blue);
            }

            .vcl-topbar-bio {
                color: var(--vcl-muted);
                font-size: var(--fs-xs);
                margin-right: auto;
            }

            .vcl-news-card {
                background: var(--vcl-card);
                border: 1px solid var(--vcl-border);
                border-radius: var(--radius);
                display: block;
                height: 100%;
                padding: var(--pad-card);
                text-decoration: none;
                transition: border-color 160ms ease, transform 160ms ease;
            }

            .vcl-news-card:hover {
                border-color: var(--vcl-blue);
                transform: translateY(-2px);
            }

            .vcl-news-source {
                color: var(--vcl-blue);
                font-size: var(--fs-2xs);
                font-weight: 800;
                letter-spacing: 0.07em;
                margin-bottom: 8px;
                text-transform: uppercase;
            }

            .vcl-news-title {
                color: var(--vcl-text);
                font-size: var(--fs-md);
                font-weight: 700;
                line-height: 1.4;
                margin-bottom: 8px;
            }

            .vcl-news-meta {
                color: var(--vcl-muted);
                font-size: var(--fs-xs);
            }

            .vcl-eyebrow {
                color: var(--vcl-blue);
                font-size: var(--fs-xs);
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
                font-size: var(--fs-xl);
                font-weight: 650;
                margin-bottom: 8px;
            }

            .vcl-copy {
                color: var(--vcl-muted);
                font-size: var(--fs-md);
                line-height: 1.7;
                max-width: 760px;
            }

            .vcl-card {
                background: var(--vcl-card);
                border: 1px solid var(--vcl-border);
                border-radius: var(--radius);
                box-shadow: 0 10px 30px rgba(17, 24, 39, 0.06);
                height: 100%;
                padding: var(--pad-card);
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
                font-size: var(--fs-2xs);
                font-weight: 800;
                letter-spacing: 0.07em;
                text-transform: uppercase;
            }

            .vcl-deal-company {
                color: var(--vcl-text);
                font-size: var(--fs-sm);
                font-weight: 750;
            }

            .vcl-deal-meta {
                color: var(--vcl-muted);
                font-size: var(--fs-xs);
            }

            .vcl-deal-dot {
                color: #C9C1B2;
            }

            .vcl-deal-score {
                font-size: var(--fs-xs);
                font-weight: 700;
            }

            .vcl-rec-banner {
                align-items: center;
                border: 1px solid;
                border-radius: var(--radius);
                display: flex;
                gap: 14px;
                margin-bottom: 24px;
                padding: var(--pad-card-tight);
            }

            .vcl-rec-dot {
                border-radius: 999px;
                flex-shrink: 0;
                height: 10px;
                width: 10px;
            }

            .vcl-rec-text {
                font-size: var(--fs-lg);
                font-weight: 820;
                letter-spacing: 0.03em;
            }

            .vcl-rec-score {
                color: var(--vcl-muted);
                font-size: var(--fs-sm);
                font-weight: 650;
            }

            .vcl-card-kicker {
                color: var(--vcl-muted);
                font-size: var(--fs-2xs);
                font-weight: 700;
                letter-spacing: 0.08em;
                margin-bottom: 12px;
                text-transform: uppercase;
            }

            .vcl-card-title {
                color: var(--vcl-text);
                font-size: var(--fs-lg);
                font-weight: 760;
                margin-bottom: 8px;
            }

            .vcl-card-body {
                color: var(--vcl-muted);
                font-size: var(--fs-sm);
                line-height: 1.55;
            }

            .vcl-icon {
                align-items: center;
                background: rgba(20, 27, 46, 0.08);
                border: 1px solid rgba(20, 27, 46, 0.25);
                border-radius: var(--radius);
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
                font-size: var(--fs-3xl);
                font-weight: 820;
                line-height: 1;
                margin-bottom: 8px;
            }

            .vcl-section {
                border-top: 1px solid var(--vcl-border);
                margin-top: 26px;
                padding-top: 20px;
            }

            .vcl-section-title {
                color: var(--vcl-text);
                font-size: var(--fs-2xl);
                font-weight: 780;
                margin-bottom: 6px;
            }

            .vcl-section-subtitle {
                color: var(--vcl-muted);
                font-size: var(--fs-sm);
                margin-bottom: 20px;
            }

            .vcl-workflow-step {
                min-height: var(--card-min-md);
            }

            .vcl-step-number {
                color: var(--vcl-blue);
                font-size: var(--fs-xs);
                font-weight: 800;
                margin-bottom: 10px;
            }


            .vcl-pill {
                border: 1px solid var(--vcl-border);
                border-radius: 999px;
                color: var(--vcl-muted);
                display: inline-flex;
                font-size: var(--fs-xs);
                font-weight: 650;
                margin: 0 8px 8px 0;
                padding: var(--pad-pill);
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
                color: #8A6420;
                font-size: var(--fs-2xs);
                font-weight: 800;
                letter-spacing: 0.08em;
                margin: 18px 0 8px;
                text-transform: uppercase;
            }

            .vcl-muted {
                color: var(--vcl-muted);
            }

            /* Side-by-side cards whose text lengths differ; without a floor
               the shorter one leaves its button hanging mid-air. */
            .vcl-card-equal { min-height: var(--card-min-lg); }

            .vcl-deal-sector-plain {
                color: var(--vcl-muted);
                font-family: 'IBM Plex Mono', monospace;
                font-size: var(--fs-xs);
                font-weight: 600;
                margin-left: 6px;
            }

            .vcl-capture {
                background: var(--vcl-blue);
                border-radius: var(--radius-lg);
                margin-top: 34px;
                padding: var(--pad-surface);
            }

            .vcl-capture .vcl-card-kicker { color: var(--vcl-gold); }
            .vcl-capture .vcl-capture-title {
                color: #FFFFFF;
                font-family: 'Fraunces', serif;
                font-size: var(--fs-2xl);
                font-weight: 700;
                margin-bottom: 6px;
            }
            .vcl-capture .vcl-card-body { color: #C7CBD6; }

            /* Most of this app's traffic arrives from a LinkedIn post, which
               means a phone. Streamlit's wide layout and three-across grids
               need explicit help below tablet width. */
            @media (max-width: 768px) {
                /* Phones shrink the scale itself rather than overriding
                   individual classes, so the hierarchy stays proportional and
                   there is still exactly one place that sets any size. */
                :root {
                    --fs-xl:  1.15rem;
                    --fs-2xl: 1.3rem;
                    --fs-3xl: 1.6rem;
                    --pad-card: 18px;
                    --pad-card-tight: 14px 16px;
                    --pad-surface: 22px 20px;
                }

                .block-container {
                    padding-left: 0.9rem;
                    padding-right: 0.9rem;
                }

                [data-testid="stHorizontalBlock"] {
                    flex-direction: column;
                    gap: 10px;
                }

                [data-testid="stHorizontalBlock"] > div,
                [data-testid="stColumn"],
                [data-testid="column"] {
                    flex: 1 1 100% !important;
                    min-width: 100% !important;
                    width: 100% !important;
                }

                .vcl-topbar {
                    flex-wrap: wrap;
                    gap: 8px;
                    justify-content: flex-start;
                }

                .vcl-topbar-bio {
                    flex-basis: 100%;
                    margin-bottom: 4px;
                    margin-right: 0;
                }

                .vcl-topbar a {
                    font-size: var(--fs-2xs);
                    padding: var(--pad-pill);
                }

                /* Fixed heights that align desktop grids just add dead space
                   once the cards are stacked. */
                .vcl-news-card, .vcl-deal-card, .vcl-workflow-step {
                    min-height: 0;
                }

            }
        </style>
        """,
        unsafe_allow_html=True,
    )


# Charts render to SVG and can't read the CSS variables, so the scale is
# mirrored here in px: 13 ≈ --fs-xs, 18 ≈ --fs-lg. Every figure in the app
# uses these so chart text matches the text around it.
CHART_FONT = dict(family="'IBM Plex Sans', sans-serif", color="#14171F", size=13)
CHART_TITLE_FONT = dict(family="'Fraunces', serif", size=18, color="#14171F")


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
