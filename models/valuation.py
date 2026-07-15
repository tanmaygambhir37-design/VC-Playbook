"""
valuation.py — Valuation Engine

Three standard early-stage valuation methods:
  1. VC Method        — back-solve pre-money from target exit value & required return
  2. Comparable Multiples — ARR x sector multiple
  3. Scorecard Method  — adjust a median regional pre-money by qualitative factors
"""

from dataclasses import dataclass


@dataclass
class VCMethodResult:
    exit_value: float
    required_multiple: float
    post_money: float
    pre_money: float
    investor_ownership_pct: float


def vc_method(exit_value_usd_m: float, target_return_multiple: float,
              investment_usd_m: float, retention_ratio: float = 0.6) -> VCMethodResult:
    """
    Classic VC Method with future-dilution adjustment:
      Post-money (future)  = Exit Value / Target Return Multiple
      Ownership at exit    = Investment / Post-money (future)
      Ownership today      = Ownership at exit / retention_ratio
                             (retention_ratio = share of ownership the investor
                             keeps through future rounds; ~0.5-0.7 is typical
                             for a seed investor holding to exit)
      Post-money (today)   = Investment / Ownership today
      Pre-money (today)    = Post-money (today) - Investment
    """
    post_money_future = exit_value_usd_m / target_return_multiple
    ownership_at_exit_pct = (investment_usd_m / post_money_future) * 100
    ownership_pct = ownership_at_exit_pct / max(retention_ratio, 0.01)
    post_money_today = investment_usd_m / (ownership_pct / 100)
    pre_money_today = post_money_today - investment_usd_m

    return VCMethodResult(
        exit_value=exit_value_usd_m,
        required_multiple=target_return_multiple,
        post_money=round(post_money_today, 2),
        pre_money=round(pre_money_today, 2),
        investor_ownership_pct=round(ownership_pct, 2),
    )


def comparable_multiples(arr_usd_m: float, sector_multiple: float,
                          illiquidity_discount_pct: float = 20.0) -> dict:
    """Comparable-company ARR multiple method with an early-stage illiquidity discount."""
    raw_valuation = arr_usd_m * sector_multiple
    discounted = raw_valuation * (1 - illiquidity_discount_pct / 100)
    return {
        "raw_valuation": round(raw_valuation, 2),
        "illiquidity_discount_pct": illiquidity_discount_pct,
        "adjusted_valuation": round(discounted, 2),
    }


# Scorecard method: qualitative factor weights vs. a median regional pre-money
SCORECARD_FACTORS = {
    "management_team": 0.30,
    "market_size": 0.25,
    "product_technology": 0.15,
    "competitive_environment": 0.10,
    "marketing_sales_channels": 0.10,
    "need_for_additional_investment": 0.05,
    "other": 0.05,
}


def scorecard_method(median_pre_money_usd_m: float, factor_scores: dict) -> dict:
    """
    factor_scores: dict of the same keys as SCORECARD_FACTORS, each a
    percentage rating vs. "typical" deal (100 = average, 150 = 50% better, etc.)
    """
    weighted_sum = sum(
        (factor_scores.get(k, 100) / 100) * w for k, w in SCORECARD_FACTORS.items()
    )
    adjusted_valuation = median_pre_money_usd_m * weighted_sum
    return {
        "adjustment_factor": round(weighted_sum, 3),
        "adjusted_pre_money": round(adjusted_valuation, 2),
    }
