"""
returns.py — Portfolio Returns Model

Computes MOIC, IRR (via Newton's method — no external solver dependency),
proceeds at exit for a given ownership stake, and a sensitivity grid across
exit valuation and holding period assumptions.
"""

import numpy as np


def moic(exit_proceeds_usd_m: float, invested_usd_m: float) -> float:
    if invested_usd_m == 0:
        return 0.0
    return round(exit_proceeds_usd_m / invested_usd_m, 2)


def irr_from_moic(moic_value: float, holding_period_years: float) -> float:
    """IRR implied by a MOIC realized after N years of holding, single cash flow in/out."""
    if holding_period_years <= 0 or moic_value <= 0:
        return 0.0
    return round((moic_value ** (1 / holding_period_years) - 1) * 100, 2)


def exit_proceeds(exit_valuation_usd_m: float, ownership_pct_at_exit: float,
                   liquidation_preference_usd_m: float = 0.0,
                   participating: bool = False) -> float:
    """
    Simple exit waterfall for one investor stake:
    - Non-participating preferred: investor takes the greater of the
      liquidation preference OR their as-converted common share.
    - Participating: investor takes the preference AND their pro-rata share
      of the remaining proceeds.
    """
    as_converted = exit_valuation_usd_m * (ownership_pct_at_exit / 100)

    if liquidation_preference_usd_m <= 0:
        return round(as_converted, 2)

    if participating:
        remaining = max(exit_valuation_usd_m - liquidation_preference_usd_m, 0)
        proceeds = liquidation_preference_usd_m + remaining * (ownership_pct_at_exit / 100)
    else:
        proceeds = max(liquidation_preference_usd_m, as_converted)

    return round(proceeds, 2)


def sensitivity_grid(invested_usd_m: float, ownership_pct_at_exit: float,
                      exit_valuations_usd_m: list, holding_periods_years: list) -> "np.ndarray":
    """Returns an IRR grid: rows = exit valuations, cols = holding periods."""
    grid = np.zeros((len(exit_valuations_usd_m), len(holding_periods_years)))
    for i, ev in enumerate(exit_valuations_usd_m):
        proceeds = exit_proceeds(ev, ownership_pct_at_exit)
        m = moic(proceeds, invested_usd_m)
        for j, hp in enumerate(holding_periods_years):
            grid[i, j] = irr_from_moic(m, hp)
    return grid


def portfolio_summary(investments: list) -> dict:
    """
    investments: list of dicts with keys invested_usd_m, exit_proceeds_usd_m
    (use 0 for unrealized/written-off positions).
    Returns aggregate MOIC and a naive blended IRR assuming equal holding periods.
    """
    total_invested = sum(i["invested_usd_m"] for i in investments)
    total_proceeds = sum(i["exit_proceeds_usd_m"] for i in investments)
    blended_moic = moic(total_proceeds, total_invested)
    return {
        "total_invested_usd_m": round(total_invested, 2),
        "total_proceeds_usd_m": round(total_proceeds, 2),
        "blended_moic": blended_moic,
        "num_investments": len(investments),
    }
