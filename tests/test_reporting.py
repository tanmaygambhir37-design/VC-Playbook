"""Tests for the memo narrative and its PDF export.

Neither module does arithmetic worth checking — the risk is that a row with
missing or odd fields raises while a user is generating a memo, and that the
PDF export drifts out of step with the narrative it is supposed to render.
"""

import pytest

from models.scoring import score_startup
from models.valuation import comparable_multiples
from services.due_diligence import (
    DueDiligenceSection,
    generate_confidence_score,
    generate_due_diligence_report,
)
from services.pdf_report import build_memo_pdf

FULL_ROW = {
    "company": "Northwind", "sector": "SaaS", "stage": "Seed",
    "business_model": "Subscription software platform", "customers": "Mid-market ops teams",
    "revenue_model": "Annual contracts", "description": "A workflow tool for logistics teams.",
    "website": "https://example.com", "competition": "Medium",
    "cac_usd": 150.0, "ltv_usd": 450.0, "mom_growth_pct": 10.0,
    "monthly_burn_usd_k": 60.0, "runway_months": 12.0, "revenue_usd_k": 200.0,
    "founder_experience_score": 6, "team_size": 15,
}


def test_report_returns_every_section_populated():
    sections = generate_due_diligence_report(FULL_ROW)
    assert len(sections) == 17
    assert all(isinstance(s, DueDiligenceSection) for s in sections)
    titles = [s.title for s in sections]
    assert len(set(titles)) == len(titles), "section titles must be unique"
    for section in sections:
        assert section.paragraph.strip()
        assert section.confidence in {"High", "Medium", "Low"}
        assert section.sources, f"{section.title} cites no sources"


def test_report_survives_a_nearly_empty_row():
    """The memo page runs this on whatever the user screened, including a row
    with almost nothing filled in."""
    sections = generate_due_diligence_report({})
    assert len(sections) == 17
    assert all(s.paragraph.strip() for s in sections)


def test_confidence_section_reports_the_live_scorecard():
    section = generate_confidence_score(FULL_ROW)
    expected = score_startup(FULL_ROW).total
    assert f"{expected}/100" in section.paragraph


def test_confidence_section_says_so_when_the_score_cannot_be_computed():
    section = generate_confidence_score({"company": "Sparse Co"})
    assert "could not be computed" in section.paragraph
    assert section.confidence == "Medium"


def test_narrative_is_flagged_as_template_text():
    """The app's honesty claim depends on this disclaimer being present."""
    section = generate_confidence_score(FULL_ROW)
    assert "template" in section.paragraph.lower()


# ------------------------------------------------------------------- PDF

def build(row=FULL_ROW):
    result = score_startup(row)
    valuation = comparable_multiples(arr_usd_m=row["revenue_usd_k"] / 1000, sector_multiple=8)
    sections = generate_due_diligence_report(row)
    return build_memo_pdf(
        row, result, valuation, sections[:6],
        ["Runway is short.", "Competition is intensifying."],
        generate_confidence_score(row),
        ["Validate CAC against the data room.", "Run two reference calls."],
    )


def test_pdf_export_produces_a_real_pdf():
    pdf = build()
    assert pdf.startswith(b"%PDF-"), "output is not a PDF"
    assert pdf.rstrip().endswith(b"%%EOF")
    assert len(pdf) > 2000, "a memo this short suggests the flowables were dropped"


def test_pdf_export_handles_a_sparse_row():
    sparse = {"company": "Sparse Co", "sector": "SaaS", "stage": "Seed",
              "cac_usd": 100.0, "ltv_usd": 300.0, "mom_growth_pct": 5.0,
              "monthly_burn_usd_k": 30.0, "runway_months": 6.0, "revenue_usd_k": 0.0,
              "founder_experience_score": 3, "team_size": 2, "competition": "High"}
    assert build(sparse).startswith(b"%PDF-")


@pytest.mark.parametrize("recommendation", ["Proceed", "Watch", "Pass"])
def test_pdf_export_renders_every_recommendation_band(recommendation):
    """Each band pulls a different colour out of RECOMMENDATION_COLORS; a
    missing key would raise only for that one band."""
    result = score_startup(FULL_ROW)
    object.__setattr__(result, "recommendation", recommendation)
    pdf = build_memo_pdf(
        FULL_ROW, result, comparable_multiples(0.2, 8),
        generate_due_diligence_report(FULL_ROW)[:3], ["A risk."],
        generate_confidence_score(FULL_ROW), ["A next step."],
    )
    assert pdf.startswith(b"%PDF-")
