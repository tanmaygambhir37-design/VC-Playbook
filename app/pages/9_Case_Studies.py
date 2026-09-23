"""Case Studies — the write-ups in reports/, rendered inside the app so readers
never leave the site (and nothing depends on the GitHub repo being public)."""

import os
import re
import sys

import streamlit as st

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(APP_DIR)
sys.path.append(APP_DIR)
sys.path.append(PROJECT_ROOT)
from components.footer import email_capture, footer
from components.navigation import sidebar
from components.theme import apply_theme, page_header
from services.analytics import track_page

REPORTS = os.path.join(PROJECT_ROOT, "reports")
STUDIES = {
    "oura": ("Oura: called before the IPO prices", "case-study-oura.md", "oura.csv"),
    "bending-spoons": ("Bending Spoons: a real IPO, checked", "case-study-bending-spoons.md", "bending_spoons.csv"),
}
_IMAGE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)[ \t]*$", re.M)
_REPO_LINK = re.compile(r"\[([^\]]+)\]\((?:\.\./)[^)]*\)")  # links into the repo -> plain text


def _prose(text: str) -> str:
    """Point cross-links at this page, drop repo-file links, and escape `$` so
    Streamlit doesn't read "$40 ... $44" as LaTeX. Code fences are left alone."""
    for key, (_, filename, _) in STUDIES.items():
        text = text.replace(f"({filename})", f"(?study={key})")
    text = _REPO_LINK.sub(r"\1", text)
    chunks = text.split("```")
    return "```".join(c if i % 2 else c.replace("$", "\\$") for i, c in enumerate(chunks))


def render(filename: str) -> None:
    with open(os.path.join(REPORTS, filename), encoding="utf-8") as f:
        parts = _IMAGE.split(f.read())  # [text, alt, src, text, alt, src, ..., text]
    for i in range(0, len(parts), 3):
        st.markdown(_prose(parts[i]))
        if i + 2 < len(parts):
            st.image(os.path.normpath(os.path.join(REPORTS, parts[i + 2])), caption=parts[i + 1] or None)


st.set_page_config(page_title="Case Studies | VC Playbook", page_icon="📗", layout="wide")
apply_theme()
sidebar()

page_header("Case Studies", "Real companies run through the simulator, written so anyone can follow.", "Reports")

keys = list(STUDIES)
requested = st.query_params.get("study", keys[0])
choice = st.radio(
    "Case study", keys, index=keys.index(requested) if requested in keys else 0,
    format_func=lambda k: STUDIES[k][0], horizontal=True, label_visibility="collapsed",
)
st.query_params["study"] = choice
track_page(f"case-studies/{choice}", STUDIES[choice][0])

render(STUDIES[choice][1])

csv_path = os.path.join(PROJECT_ROOT, "data", "case_studies", STUDIES[choice][2])
if os.path.exists(csv_path):
    with open(csv_path, "rb") as f:
        st.download_button(
            "Download the inputs (CSV) to run it yourself", f.read(),
            file_name=STUDIES[choice][2], mime="text/csv",
        )

email_capture()
footer()
