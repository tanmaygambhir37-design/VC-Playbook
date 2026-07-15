"""
scoring.py — VC Scorecard Model

Implements a weighted scoring framework loosely based on how seed/Series A
investors triage deals: unit economics, growth, market/competition, team,
and runway/burn discipline. Produces a 0-100 VC Score plus a Proceed /
Watch / Pass recommendation and per-dimension breakdown for a radar chart.
"""

from dataclasses import dataclass


WEIGHTS = {
    "unit_economics": 0.30,   # LTV:CAC
    "growth": 0.25,           # MoM revenue growth
    "market": 0.15,           # competition intensity (inverse)
    "team": 0.20,             # founder experience + team size sanity
    "efficiency": 0.10,       # burn multiple / runway
}

COMPETITION_SCORE = {"Low": 90, "Medium": 60, "High": 35}


@dataclass
class ScoreResult:
    total: float
    breakdown: dict
    recommendation: str
    strengths: list
    weaknesses: list


def _clip(x, lo=0, hi=100):
    return max(lo, min(hi, x))


def score_unit_economics(cac: float, ltv: float) -> float:
    if cac <= 0:
        return 50.0
    ratio = ltv / cac
    # 3x LTV:CAC is the classic "healthy" benchmark -> maps to ~75
    # scale so 1x -> ~25, 3x -> ~75, 6x+ -> ~100
    return _clip(15 + ratio * 20)


def score_growth(mom_growth_pct: float, stage: str) -> float:
    # Benchmarks anchored to YC guidance (~5-7%/week exceptional, 1-2%/week
    # good => roughly 5-10% MoM for a solid early-stage company). Hitting the
    # benchmark scores 50; each point above/below moves the score by 3.
    benchmarks = {"Pre-Seed": 10, "Seed": 8, "Series A": 6}
    target = benchmarks.get(stage, 8)
    return _clip(50 + (mom_growth_pct - target) * 3)


def score_market(competition: str) -> float:
    return COMPETITION_SCORE.get(competition, 50)


def score_team(founder_experience_score: int, team_size: int) -> float:
    exp_component = founder_experience_score * 8   # 1-10 -> 8-80
    size_component = _clip(team_size * 1.2, hi=20)  # small bonus for having a real team
    return _clip(exp_component * 0.8 + size_component)


def score_efficiency(monthly_burn_usd_k: float, runway_months: float, revenue_usd_k: float,
                     mom_growth_pct: float = 10.0) -> float:
    runway_score = _clip(runway_months * 5)

    # Pre-revenue: a burn multiple is meaningless, so score on runway alone.
    if revenue_usd_k < 1:
        return runway_score

    # Burn multiple (Sacks): net burn / net new ARR.
    # Net new ARR per month ~= current ARR * MoM growth rate.
    net_new_arr_usd_k = revenue_usd_k * (mom_growth_pct / 100)
    burn_multiple = monthly_burn_usd_k / max(net_new_arr_usd_k, 1)
    # Sacks bands: <1x amazing, 1-2x good, 2-3x suboptimal, >3x concerning
    burn_score = _clip(100 - burn_multiple * 25)
    return _clip((burn_score + runway_score) / 2)


def score_startup(row: dict) -> ScoreResult:
    dims = {
        "unit_economics": score_unit_economics(row["cac_usd"], row["ltv_usd"]),
        "growth": score_growth(row["mom_growth_pct"], row["stage"]),
        "market": score_market(row["competition"]),
        "team": score_team(row["founder_experience_score"], row["team_size"]),
        "efficiency": score_efficiency(
            row["monthly_burn_usd_k"], row["runway_months"], row["revenue_usd_k"],
            row.get("mom_growth_pct", 10.0),
        ),
    }

    total = sum(dims[k] * WEIGHTS[k] for k in WEIGHTS)
    total = round(_clip(total), 1)

    if total >= 75:
        rec = "Proceed"
    elif total >= 55:
        rec = "Watch"
    else:
        rec = "Pass"

    ranked = sorted(dims.items(), key=lambda x: x[1], reverse=True)
    labels = {
        "unit_economics": "Unit Economics (LTV:CAC)",
        "growth": "Revenue Growth",
        "market": "Market / Competitive Position",
        "team": "Founding Team",
        "efficiency": "Burn Efficiency & Runway",
    }
    strengths = [labels[k] for k, v in ranked if v >= 65][:3]
    weaknesses = [labels[k] for k, v in ranked if v < 50][:3]

    return ScoreResult(total=total, breakdown=dims, recommendation=rec,
                        strengths=strengths, weaknesses=weaknesses)
