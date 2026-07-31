"""Tests for the news -> scorecard bridge and the share-link codec."""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for path in (os.path.join(ROOT, "app"), ROOT):
    if path not in sys.path:
        sys.path.insert(0, path)

import pytest

from models.prefill import (
    STAGE_BENCHMARKS,
    arr_multiple_for,
    build_prefill_row,
    parse_amount,
    stage_from_round,
)
from models.scoring import score_startup
from services.share import decode_row, encode_row


@pytest.mark.parametrize("text,expected", [
    ("$570M", 570.0),
    ("$1.7B", 1700.0),
    ("€4.2M", 4.2),
    ("£70 million", 70.0),
    ("$100 billion", 100_000.0),
    ("$800k", 0.8),
    ("$1,200M", 1200.0),   # thousands separator, not a decimal comma
    ("€4,2M", 4.2),        # decimal comma
    ("", None),
    ("Series C", None),
])
def test_parse_amount(text, expected):
    assert parse_amount(text) == expected


@pytest.mark.parametrize("label,amount,expected", [
    ("Series C", 570.0, "Growth"),
    ("Series A", 12.0, "Series A"),
    ("Pre-Seed", None, "Pre-Seed"),
    ("seed", 4.0, "Seed"),
    ("Growth round", None, "Growth"),
    ("Early stage", 100.0, "Growth"),   # vague label falls back to size
    ("Early stage", 2.0, "Pre-Seed"),
    ("", None, "Seed"),                 # nothing known at all
])
def test_stage_from_round(label, amount, expected):
    assert stage_from_round(label, amount) == expected


def test_sector_aliases_agree():
    """A headline tagged "AI" and a dataset row tagged "DeepTech / AI" must
    price off the same multiple."""
    assert arr_multiple_for("AI") == arr_multiple_for("DeepTech / AI")
    assert arr_multiple_for("fintech") == arr_multiple_for("Fintech")
    assert arr_multiple_for("Nonexistent Sector") == 8.0


def test_build_prefill_row_is_immediately_scoreable():
    row, assumed = build_prefill_row({
        "company": "Multiverse Computing", "sector": "AI",
        "round": "Series C", "amount": "$570M",
        "note": "Spanish AI model-compression startup.",
    })

    assert row["company"] == "Multiverse Computing"
    assert row["stage"] == "Growth"
    assert row["sector_median_arr_multiple"] == arr_multiple_for("AI")
    assert "model-compression" in row["description"]
    assert assumed, "the UI needs the list of assumed fields to disclose them"

    # The point of the prefill: score_startup runs on it without further input.
    result = score_startup(row)
    assert 0 <= result.total <= 100
    assert result.recommendation in {"Proceed", "Watch", "Pass"}


@pytest.mark.parametrize("stage", list(STAGE_BENCHMARKS))
def test_every_stage_benchmark_lands_mid_range(stage):
    """Benchmarks should start a deal as arguable, not as an automatic
    Proceed or Pass — otherwise the first thing a visitor sees is a verdict
    the numbers didn't earn."""
    row, _ = build_prefill_row({"company": "X", "sector": "SaaS", "stage": stage})
    assert score_startup(row).recommendation == "Watch"


def test_share_round_trip_preserves_inputs():
    row = {
        "company": "Linked Co", "sector": "Fintech", "stage": "Seed",
        "description": "A company.", "revenue_usd_k": 123.5,
        "mom_growth_pct": 9.0, "cac_usd": 210.0, "ltv_usd": 900.0,
        "monthly_burn_usd_k": 130.0, "runway_months": 14.0,
        "competition": "Medium", "founder_experience_score": 7,
        "team_size": 20, "sector_median_arr_multiple": 7.5,
    }
    restored = decode_row(encode_row(row))
    assert restored == row
    assert score_startup(restored).total == score_startup(row).total


@pytest.mark.parametrize("token", [
    "", "not-a-token", "!!!!", "a" * 5000,
    encode_row({"company": "X"})[:-6],   # truncated in transit
])
def test_bad_share_tokens_decode_to_none(token):
    assert decode_row(token) is None


def test_share_token_ignores_unknown_fields():
    """Links come from the address bar, so a hand-edited payload must not be
    able to push arbitrary keys into the screening row."""
    import base64
    import json
    import zlib

    payload = json.dumps({"company": "X", "is_admin": True, "revenue_usd_k": "12"}).encode()
    token = base64.urlsafe_b64encode(zlib.compress(payload)).decode().rstrip("=")
    restored = decode_row(token)

    assert "is_admin" not in restored
    assert restored["revenue_usd_k"] == 12.0   # coerced to the declared type
