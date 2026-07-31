"""share.py — encode a screening analysis into a link.

The memo already produces a PDF, but a downloaded file is not something anyone
can post. A link is. This packs the screening inputs into a single URL
parameter so an analysis can be shared, reopened, and argued with.

The payload is zlib-compressed JSON in URL-safe base64 — compact enough for a
usable link, and self-contained, so there is no database and no expiry.
"""

import base64
import json
import zlib

# Only these travel in a link. Anything else in the row is ignored on the way
# out and dropped on the way in, so a hand-edited link can't inject fields.
SHAREABLE_FIELDS = (
    "company", "sector", "stage", "business_model", "customers", "location",
    "website", "founding_year", "revenue_model", "description",
    "revenue_usd_k", "mom_growth_pct", "cac_usd", "ltv_usd",
    "monthly_burn_usd_k", "runway_months", "competition",
    "founder_experience_score", "team_size", "sector_median_arr_multiple",
)

_NUMERIC = {
    "revenue_usd_k": float, "mom_growth_pct": float, "cac_usd": float,
    "ltv_usd": float, "monthly_burn_usd_k": float, "runway_months": float,
    "sector_median_arr_multiple": float, "founder_experience_score": int,
    "team_size": int,
}

MAX_TOKEN_CHARS = 4000


def encode_row(row: dict) -> str:
    """Pack a screening row into a URL-safe token."""
    payload = {k: row[k] for k in SHAREABLE_FIELDS if k in row and row[k] != ""}
    raw = json.dumps(payload, separators=(",", ":"), default=str).encode()
    return base64.urlsafe_b64encode(zlib.compress(raw, 9)).decode().rstrip("=")


def decode_row(token: str) -> dict | None:
    """Unpack a token back into a screening row, or None if it isn't one.

    Tokens arrive from the address bar, so this treats every failure mode —
    truncated link, wrong field types, someone's hand-edited payload — as
    "no prefill" rather than an error page.
    """
    if not token or len(token) > MAX_TOKEN_CHARS:
        return None
    try:
        padded = token + "=" * (-len(token) % 4)
        raw = zlib.decompress(base64.urlsafe_b64decode(padded.encode()))
        payload = json.loads(raw)
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None

    row = {}
    for key in SHAREABLE_FIELDS:
        if key not in payload:
            continue
        value = payload[key]
        caster = _NUMERIC.get(key)
        if caster is None:
            row[key] = str(value)[:400]
            continue
        try:
            row[key] = caster(value)
        except (TypeError, ValueError):
            continue
    return row or None
