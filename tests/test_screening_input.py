"""Tests for CSV intake coercion.

Every case here is a cell shape a hand-edited spreadsheet actually produces.
Before coercion existed they reached a Streamlit widget directly and raised
mid-render, so the page died with a traceback instead of an explanation.
"""

import pytest

from models.scoring import score_startup
from services.screening_input import (
    DEFAULT_SCREENING,
    SCREENING_BOUNDS,
    coerce_screening,
    to_company_payload,
)


def test_a_clean_row_passes_through_unchanged():
    row = dict(DEFAULT_SCREENING)
    screening, notes = coerce_screening(row)
    assert screening == DEFAULT_SCREENING
    assert notes == []


@pytest.mark.parametrize("bad", ["N/A", "", "  ", "unknown", None, "TBD"])
def test_non_numeric_cells_fall_back_to_the_default(bad):
    screening, notes = coerce_screening({**DEFAULT_SCREENING, "revenue_usd_k": bad})
    assert screening["revenue_usd_k"] == DEFAULT_SCREENING["revenue_usd_k"]
    assert any("revenue_usd_k" in note for note in notes)


def test_thousands_separators_are_read_as_numbers():
    screening, notes = coerce_screening({**DEFAULT_SCREENING, "cac_usd": "1,200"})
    assert screening["cac_usd"] == 1200.0
    assert notes == []


def test_out_of_range_values_are_clamped_not_rejected():
    screening, notes = coerce_screening({**DEFAULT_SCREENING, "runway_months": 999})
    assert screening["runway_months"] == SCREENING_BOUNDS["runway_months"][1]
    assert any("clamped" in note for note in notes)

    screening, notes = coerce_screening({**DEFAULT_SCREENING, "cac_usd": -50})
    assert screening["cac_usd"] == SCREENING_BOUNDS["cac_usd"][0]
    assert any("clamped" in note for note in notes)


def test_every_numeric_field_lands_inside_its_widget_bounds():
    """The invariant that keeps the form from raising: whatever comes in, what
    comes out is renderable."""
    hostile = dict.fromkeys(SCREENING_BOUNDS, "garbage")
    hostile["competition"] = "???"
    screening, _ = coerce_screening(hostile)
    for key, (low, high) in SCREENING_BOUNDS.items():
        assert low <= screening[key] <= high, f"{key} escaped its bounds"

    huge = dict.fromkeys(SCREENING_BOUNDS, 10 ** 12)
    screening, _ = coerce_screening(huge)
    for key, (low, high) in SCREENING_BOUNDS.items():
        assert low <= screening[key] <= high, f"{key} escaped its bounds"


def test_integer_fields_stay_integers():
    screening, _ = coerce_screening({**DEFAULT_SCREENING, "team_size": "42.7", "founder_experience_score": "7.9"})
    assert isinstance(screening["team_size"], int)
    assert isinstance(screening["founder_experience_score"], int)


@pytest.mark.parametrize("raw,expected", [("low", "Low"), ("HIGH", "High"), ("Medium", "Medium")])
def test_competition_is_normalized(raw, expected):
    screening, notes = coerce_screening({**DEFAULT_SCREENING, "competition": raw})
    assert screening["competition"] == expected
    assert notes == []


def test_unknown_competition_falls_back_with_a_note():
    screening, notes = coerce_screening({**DEFAULT_SCREENING, "competition": "Fierce"})
    assert screening["competition"] == DEFAULT_SCREENING["competition"]
    assert any("competition" in note for note in notes)


def test_missing_columns_use_defaults():
    screening, notes = coerce_screening({})
    assert screening == DEFAULT_SCREENING
    assert notes == []


def test_a_coerced_row_can_always_be_scored():
    """The whole point: a hostile CSV produces a score instead of a traceback."""
    hostile = {"company": "Junk Co", "sector": "SaaS", "stage": "Seed",
               "revenue_usd_k": "N/A", "mom_growth_pct": "", "cac_usd": "1,200",
               "ltv_usd": None, "monthly_burn_usd_k": "lots", "runway_months": 999,
               "competition": "???", "founder_experience_score": "11",
               "team_size": "-4", "sector_median_arr_multiple": "eight"}
    screening, notes = coerce_screening(hostile)
    result = score_startup({**to_company_payload(hostile), **screening})
    assert 0 <= result.total <= 100
    assert result.recommendation in {"Proceed", "Watch", "Pass"}
    assert notes, "the user should be told what was substituted"


def test_to_company_payload_fills_gaps_and_stringifies_the_year():
    payload = to_company_payload({"company": "Acme", "founding_year": 2019})
    assert payload["company"] == "Acme"
    assert payload["founding_year"] == "2019"
    assert payload["sector"]  # defaulted rather than missing
