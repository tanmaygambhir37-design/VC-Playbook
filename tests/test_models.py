"""Core sanity tests for the financial models."""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.cap_table import simulate_rounds
from models.returns import exit_proceeds, irr_from_moic, moic
from models.scoring import score_startup
from models.valuation import comparable_multiples, scorecard_method, vc_method


SAMPLE_ROW = {
    "cac_usd": 150.0,
    "ltv_usd": 450.0,
    "mom_growth_pct": 10.0,
    "stage": "Seed",
    "competition": "Medium",
    "founder_experience_score": 6,
    "team_size": 15,
    "monthly_burn_usd_k": 60.0,
    "runway_months": 12.0,
    "revenue_usd_k": 200.0,
}


def test_cap_table_sums_to_100_after_every_round():
    snapshots = simulate_rounds(
        founder_pct=90,
        esop_pct=10,
        rounds=[
            {"name": "Seed", "pre_money_usd_m": 8, "investment_usd_m": 2, "esop_topup_pct": 5},
            {"name": "Series A", "pre_money_usd_m": 30, "investment_usd_m": 10},
            {"name": "Series B", "pre_money_usd_m": 90, "investment_usd_m": 30, "esop_topup_pct": 3},
        ],
    )
    for snap in snapshots:
        assert sum(snap["cap_table"].values()) == pytest.approx(100, abs=1e-6)
    # each round must dilute the founders
    founder_series = [s["cap_table"]["Founders"] for s in snapshots]
    assert founder_series == sorted(founder_series, reverse=True)


def test_moic_and_irr_math():
    assert moic(40, 10) == 4.0
    # 4x over 4 years = 41.42% IRR (2^(1/2)-1)
    assert irr_from_moic(4.0, 4) == pytest.approx(41.42, abs=0.01)
    assert irr_from_moic(1.0, 5) == 0.0  # money back = 0% IRR
    assert irr_from_moic(0, 5) == 0.0    # guard: total loss


def test_exit_waterfall_non_participating_takes_greater():
    # 10% of $50M = $5M as-converted < $8M preference -> take preference
    assert exit_proceeds(50, 10, liquidation_preference_usd_m=8, participating=False) == 8
    # 10% of $200M = $20M > $8M preference -> convert
    assert exit_proceeds(200, 10, liquidation_preference_usd_m=8, participating=False) == 20


def test_exit_waterfall_participating_stacks():
    # preference + pro-rata of remainder: 8 + 10% * (50-8) = 12.2
    assert exit_proceeds(50, 10, liquidation_preference_usd_m=8, participating=True) == pytest.approx(12.2)


def test_vc_method_retention_lowers_todays_valuation():
    full = vc_method(300, 10, 2, retention_ratio=1.0)
    diluted = vc_method(300, 10, 2, retention_ratio=0.6)
    # with future dilution expected, the investor needs MORE ownership today,
    # so today's implied valuation must be LOWER
    assert diluted.investor_ownership_pct > full.investor_ownership_pct
    assert diluted.post_money < full.post_money
    assert diluted.pre_money == pytest.approx(diluted.post_money - 2, abs=0.01)


def test_comparable_multiples_discount():
    res = comparable_multiples(arr_usd_m=2, sector_multiple=10, illiquidity_discount_pct=20)
    assert res["raw_valuation"] == 20
    assert res["adjusted_valuation"] == 16


def test_scorecard_method_average_deal_is_median():
    res = scorecard_method(5.0, {})  # all factors default to 100 = average
    assert res["adjusted_pre_money"] == pytest.approx(5.0)


def test_score_startup_bounds_and_recommendation():
    result = score_startup(SAMPLE_ROW)
    assert 0 <= result.total <= 100
    assert result.recommendation in {"Proceed", "Watch", "Pass"}
    assert set(result.breakdown) == {"unit_economics", "growth", "market", "team", "efficiency"}
