"""screening_input.py — the intake contract for the scorecard.

Defines the screening fields, their defaults, and the range each one may take,
plus the coercion that turns an arbitrary CSV row into values the form widgets
can render. Kept out of the page module so it can be tested without Streamlit.
"""

import pandas as pd

DEFAULT_COMPANY = {
    "company": "New Startup",
    "sector": "SaaS",
    "stage": "Seed",
    "business_model": "Subscription software platform",
    "customers": "Mid-market companies",
    "location": "San Francisco, CA",
    "website": "",
    "founding_year": "2023",
    "revenue_model": "Monthly subscription",
    "description": "Early-stage company building a focused software product for a defined customer segment.",
}

DEFAULT_SCREENING = {
    "revenue_usd_k": 20.0,
    "mom_growth_pct": 10.0,
    "cac_usd": 150.0,
    "ltv_usd": 450.0,
    "monthly_burn_usd_k": 60.0,
    "runway_months": 12.0,
    "competition": "Medium",
    "founder_experience_score": 6,
    "team_size": 15,
    "sector_median_arr_multiple": 8.0,
}

COMPETITION_OPTIONS = ["Low", "Medium", "High"]

STAGES = ["Pre-Seed", "Seed", "Series A", "Growth"]

# (min, max) for every numeric screening field. The form widgets and the CSV
# importer both read these, so an imported value can never land outside the
# range its own widget will accept.
SCREENING_BOUNDS = {
    "revenue_usd_k": (0.0, 5_000_000.0),
    "mom_growth_pct": (0.0, 100.0),
    "cac_usd": (1.0, 5_000.0),
    "ltv_usd": (1.0, 20_000.0),
    "monthly_burn_usd_k": (1.0, 500_000.0),
    "runway_months": (0.0, 48.0),
    "founder_experience_score": (1, 10),
    "team_size": (1, 20_000),
    "sector_median_arr_multiple": (1.0, 50.0),
}

SCREENING_COLUMNS = [
    "company", "sector", "stage", "business_model", "customers", "location",
    "website", "founding_year", "revenue_model", "description",
    "revenue_usd_k", "mom_growth_pct", "cac_usd", "ltv_usd",
    "monthly_burn_usd_k", "runway_months", "competition",
    "founder_experience_score", "team_size", "sector_median_arr_multiple",
]


def to_company_payload(row: dict) -> dict:
    """Pull the descriptive (non-numeric) fields off a row, filling any gaps."""
    payload = {key: row.get(key, default) for key, default in DEFAULT_COMPANY.items()}
    payload["founding_year"] = str(payload["founding_year"])
    return payload


def coerce_screening(row: dict) -> tuple[dict, list[str]]:
    """Map a raw row onto screening inputs the form can actually render.

    A hand-edited CSV routinely carries blanks, "N/A", "1,200", or a number far
    outside the widget's range. Each of those used to raise before the page
    finished rendering, so instead: non-numeric cells fall back to the default
    and out-of-range numbers are clamped. Returns (screening, notes) where
    notes describes every substitution made.
    """
    screening: dict = {}
    notes: list[str] = []

    for key, default in DEFAULT_SCREENING.items():
        raw = row.get(key, default)

        if key == "competition":
            value = str(raw).strip().title()
            if value not in COMPETITION_OPTIONS:
                notes.append(f"`competition` was {raw!r} — expected Low, Medium, or High. Using {default}.")
                value = default
            screening[key] = value
            continue

        low, high = SCREENING_BOUNDS[key]
        # Strip thousands separators before parsing: "1,200" is a number here.
        if isinstance(raw, str):
            raw = raw.replace(",", "").strip()
        value = pd.to_numeric(raw, errors="coerce")

        if pd.isna(value):
            notes.append(f"`{key}` was not a number ({row.get(key)!r}) — using the default {default}.")
            screening[key] = default
            continue

        clamped = min(max(float(value), low), high)
        if clamped != float(value):
            notes.append(
                f"`{key}` was {float(value):g}, outside the supported {low:g}–{high:g} range — clamped to {clamped:g}."
            )
        screening[key] = type(default)(clamped)

    return screening, notes
