"""
prefill.py — turn a news headline or curated deal into a screenable profile.

The news wall knows four things about a deal: company, sector, round label,
and amount raised. A scorecard needs fifteen. This module bridges that gap so
"analyze this deal" lands the reader on a filled scorecard they can argue with
instead of an empty form they will abandon.

Everything this produces is an assumption, and the caller gets back the list of
fields that were assumed so the UI can say so plainly. Editing a wrong number
is a far better first interaction than typing fifteen right ones.

Stage benchmarks are deliberately hand-specified rather than derived from
data/startups.csv: that dataset is randomly generated, so its Pre-Seed rows
carry larger teams and faster growth than its Series A rows. Growth rates are
anchored to the same YC-derived targets score_growth() uses (Pre-Seed ~10%,
Seed ~8%, Series A ~6% MoM), and LTV:CAC sits just above the 3x benchmark so a
prefilled company starts mid-range rather than flattering or damning itself.
"""

import re

# Operating profile of a typical company at each entry stage.
STAGE_BENCHMARKS = {
    "Pre-Seed": {
        "revenue_usd_k": 10.0, "mom_growth_pct": 10.0, "cac_usd": 120.0,
        "ltv_usd": 400.0, "monthly_burn_usd_k": 45.0, "runway_months": 15.0,
        "team_size": 6, "founder_experience_score": 6, "competition": "Medium",
    },
    "Seed": {
        "revenue_usd_k": 75.0, "mom_growth_pct": 8.0, "cac_usd": 200.0,
        "ltv_usd": 700.0, "monthly_burn_usd_k": 120.0, "runway_months": 15.0,
        "team_size": 18, "founder_experience_score": 6, "competition": "Medium",
    },
    "Series A": {
        "revenue_usd_k": 500.0, "mom_growth_pct": 6.0, "cac_usd": 500.0,
        "ltv_usd": 1800.0, "monthly_burn_usd_k": 450.0, "runway_months": 18.0,
        "team_size": 55, "founder_experience_score": 7, "competition": "Medium",
    },
    "Growth": {
        "revenue_usd_k": 4000.0, "mom_growth_pct": 4.0, "cac_usd": 1200.0,
        "ltv_usd": 4800.0, "monthly_burn_usd_k": 1800.0, "runway_months": 20.0,
        "team_size": 220, "founder_experience_score": 8, "competition": "High",
    },
}

# Sector ARR multiples. Dataset sector names and the shorter labels the news
# extractor produces both resolve here, so a headline tagged "AI" and a CSV row
# tagged "DeepTech / AI" price off the same number.
SECTOR_ARR_MULTIPLES = {
    "SaaS": 14.6, "SOFTWARE": 14.6,
    "DeepTech / AI": 12.1, "AI": 12.1, "ROBOTICS": 11.0, "SPACE": 10.0,
    "Consumer Internet": 12.3, "CONSUMER": 12.3,
    "ClimateTech": 11.1, "CLIMATE": 11.1, "ENERGY": 11.1,
    "HealthTech": 10.0, "HEALTH": 10.0, "BIOTECH": 10.0,
    "AgriTech": 8.1, "Fintech": 7.5, "FINTECH": 7.5, "CRYPTO": 7.5,
    "D2C": 7.6, "Logistics": 6.7, "DEFENSE": 9.0, "EdTech": 4.2,
}
DEFAULT_ARR_MULTIPLE = 8.0

# Round size (USD millions) -> stage, used when the round label is missing or
# vague ("early stage", "growth round").
_AMOUNT_STAGE_BANDS = ((3.0, "Pre-Seed"), (15.0, "Seed"), (50.0, "Series A"))

_ROUND_PATTERNS = (
    (r"pre[\s-]?seed", "Pre-Seed"),
    (r"series\s*a\b", "Series A"),
    (r"series\s*[b-z]\b|growth|late[\s-]?stage|pre[\s-]?ipo|mezzanine", "Growth"),
    (r"\bseed\b", "Seed"),
)

_AMOUNT_RE = re.compile(
    r"(?P<currency>[$€£])?\s*(?P<value>\d+(?:[.,]\d+)?)\s*"
    r"(?P<unit>billion|million|bn|[mbk])?",
    re.IGNORECASE,
)

_UNIT_MULTIPLIERS = {"b": 1000.0, "bn": 1000.0, "billion": 1000.0,
                     "m": 1.0, "million": 1.0, "k": 0.001}


def parse_amount(text: str) -> float | None:
    """Round size in millions of the quoted currency, or None.

    No FX conversion is applied — a €4.2M round is returned as 4.2. That is
    accurate enough for picking a stage band and avoids inventing a rate that
    would go stale.
    """
    if not text:
        return None
    match = _AMOUNT_RE.search(str(text))
    if not match:
        return None
    # "$1,200M" is twelve hundred million; "€4,2M" is four point two.
    raw = re.sub(r",(?=\d{3}\b)", "", match.group("value")).replace(",", ".")
    try:
        value = float(raw)
    except ValueError:
        return None
    unit = (match.group("unit") or "m").lower()
    return round(value * _UNIT_MULTIPLIERS.get(unit, 1.0), 3)


def stage_from_round(round_label: str = "", amount_musd: float | None = None) -> str:
    """Entry stage from an explicit round label, falling back to round size."""
    label = (round_label or "").lower()
    for pattern, stage in _ROUND_PATTERNS:
        if re.search(pattern, label):
            return stage
    if amount_musd is not None:
        for ceiling, stage in _AMOUNT_STAGE_BANDS:
            if amount_musd < ceiling:
                return stage
        return "Growth"
    return "Seed"


def arr_multiple_for(sector: str) -> float:
    if not sector:
        return DEFAULT_ARR_MULTIPLE
    if sector in SECTOR_ARR_MULTIPLES:
        return SECTOR_ARR_MULTIPLES[sector]
    upper = sector.strip().upper()
    for key, multiple in SECTOR_ARR_MULTIPLES.items():
        if key.upper() == upper:
            return multiple
    return DEFAULT_ARR_MULTIPLE


# Operating metrics a headline never reports — every one of these is a
# benchmark stand-in, and the UI names them so the reader knows to overwrite.
ASSUMED_FIELD_LABELS = {
    "revenue_usd_k": "Revenue (ARR)", "mom_growth_pct": "MoM growth",
    "cac_usd": "CAC", "ltv_usd": "LTV", "monthly_burn_usd_k": "Monthly burn",
    "runway_months": "Runway", "team_size": "Team size",
    "founder_experience_score": "Founder experience",
    "competition": "Competition", "sector_median_arr_multiple": "Sector ARR multiple",
}


def build_prefill_row(deal: dict) -> tuple[dict, list[str]]:
    """Expand a news/curated deal into a full screening row.

    Returns (row, assumed_labels) where assumed_labels names every operating
    metric that came from the stage benchmark rather than the deal itself.
    """
    deal = deal or {}
    amount_musd = parse_amount(deal.get("amount", ""))
    stage = deal.get("stage") or stage_from_round(deal.get("round", ""), amount_musd)
    if stage not in STAGE_BENCHMARKS:
        stage = "Seed"

    sector = deal.get("sector") or "SaaS"
    benchmark = STAGE_BENCHMARKS[stage]

    raised = f" Raised {deal['amount']}" if deal.get("amount") else ""
    round_label = f" ({deal['round']})" if deal.get("round") else ""
    note = (deal.get("note") or "").strip()
    description = note or (
        f"{deal.get('company', 'This company')} is a {sector} company at "
        f"{stage} stage.{raised}{round_label}".strip()
    )

    row = {
        "company": deal.get("company", "New Startup"),
        "sector": sector,
        "stage": stage,
        "business_model": f"{sector} company",
        "customers": "Not yet specified",
        "location": deal.get("location", ""),
        "website": deal.get("link", ""),
        "founding_year": "",
        "revenue_model": "Not yet specified",
        "description": description,
        "sector_median_arr_multiple": arr_multiple_for(sector),
        **benchmark,
    }

    return row, list(ASSUMED_FIELD_LABELS.values())
