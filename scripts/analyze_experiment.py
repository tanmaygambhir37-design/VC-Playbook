"""Analyze the VC Playbook experiments.

A/B mode (Experiment 01) — four counts, two-proportion z-test:

    python scripts/analyze_experiment.py --landing-a 120 --val-a 18 \
                                         --landing-b 115 --val-b 25

Channels mode (Experiment 02) — a GoatCounter CSV export, per-channel funnel:

    python scripts/analyze_experiment.py --channels export.csv

Everything here is stdlib. Phi() is the normal CDF via math.erf.
"""

import argparse
import csv
import math
import re


def phi(z: float) -> float:
    """Standard-normal CDF."""
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def two_proportion_z(c_a: int, n_a: int, c_b: int, n_b: int) -> dict:
    """Two-sided two-proportion z-test for conversion B vs A."""
    if n_a == 0 or n_b == 0:
        return {"rate_a": None, "rate_b": None, "z": None, "p_value": None, "verdict": "no data"}
    p_a, p_b = c_a / n_a, c_b / n_b
    pooled = (c_a + c_b) / (n_a + n_b)
    se = math.sqrt(pooled * (1 - pooled) * (1 / n_a + 1 / n_b))
    if se == 0:
        return {"rate_a": p_a, "rate_b": p_b, "z": 0.0, "p_value": 1.0, "verdict": "no variance"}
    z = (p_b - p_a) / se
    p_value = 2 * (1 - phi(abs(z)))
    verdict = "significant (p<0.05)" if p_value < 0.05 else "inconclusive"
    return {"rate_a": p_a, "rate_b": p_b, "z": z, "p_value": p_value, "verdict": verdict}


def report(c_a: int, n_a: int, c_b: int, n_b: int) -> str:
    r = two_proportion_z(c_a, n_a, c_b, n_b)
    if r["rate_a"] is None:
        return "Not enough data yet — both arms need landing visits."
    lift = (r["rate_b"] - r["rate_a"]) * 100
    return (
        f"A (control):   {c_a}/{n_a} = {r['rate_a']*100:.1f}% completed a valuation\n"
        f"B (treatment): {c_b}/{n_b} = {r['rate_b']*100:.1f}% completed a valuation\n"
        f"Absolute lift: {lift:+.1f} pts   |   z = {r['z']:.2f}   p = {r['p_value']:.3f}\n"
        f"Verdict: {r['verdict']}"
    )


# --------------------------------------------------------------- channels (Exp 02)

_SRC_PATH = re.compile(r"^/?src/([a-z0-9-]{1,20})/(landing|valuation)$")
_COUNT_HEADERS = {"count", "visits", "hits", "pageviews", "unique", "unique count", "pageview"}


def _path_column(fieldnames) -> str | None:
    for name in fieldnames or []:
        if name and "path" in name.strip().lower():
            return name
    return None


def _count_column(fieldnames) -> str | None:
    for name in fieldnames or []:
        if name and name.strip().lower() in _COUNT_HEADERS:
            return name
    return None


def parse_channels_csv(source, exclude=("test",)) -> dict:
    """Sum /src/<channel>/<stage> counts from a GoatCounter CSV export.

    Accepts a path or a file-like object. If the export has a count column it's
    summed; otherwise each row counts as one hit (the per-hit export format).
    `exclude` drops our own check traffic (e.g. ref=test).
    """
    close = not hasattr(source, "read")
    f = open(source, newline="") if close else source
    try:
        reader = csv.DictReader(f)
        path_col = _path_column(reader.fieldnames)
        count_col = _count_column(reader.fieldnames)
        counts: dict = {}
        for row in reader:
            match = _SRC_PATH.match((row.get(path_col) or "").strip()) if path_col else None
            if not match:
                continue
            channel, stage = match.group(1), match.group(2)
            if channel in exclude:
                continue
            n = 1
            if count_col:
                try:
                    n = int(float(row.get(count_col) or 0))
                except ValueError:
                    n = 0
            bucket = counts.setdefault(channel, {"landing": 0, "valuation": 0})
            bucket[stage] += n
        return counts
    finally:
        if close:
            f.close()


def channels_report(counts: dict, min_sessions: int = 30) -> str:
    lines = [f"{'channel':<12}{'sessions':>10}{'completions':>14}{'rate':>9}", "-" * 45]
    for ch in sorted(counts, key=lambda k: (counts[k]["valuation"], counts[k]["landing"]), reverse=True):
        landing, val = counts[ch]["landing"], counts[ch]["valuation"]
        rate = f"{val / landing * 100:.1f}%" if landing else "—"
        mark = "" if landing >= min_sessions else "   (below threshold)"
        lines.append(f"{ch:<12}{landing:>10}{val:>14}{rate:>9}{mark}")

    eligible = {c: v for c, v in counts.items() if v["landing"] >= min_sessions}
    if not eligible:
        verdict = (f"inconclusive: distribution is still the bottleneck "
                   f"(no channel reached {min_sessions} landing sessions)")
    else:
        winner = max(
            eligible,
            key=lambda k: (eligible[k]["valuation"],
                           eligible[k]["valuation"] / eligible[k]["landing"] if eligible[k]["landing"] else 0),
        )
        dropped = sorted(c for c in counts if counts[c]["landing"] < min_sessions)
        verdict = f"winner: {winner} — most valuation completions among channels with >= {min_sessions} sessions. Double down on {winner}"
        if dropped:
            verdict += f"; drop {', '.join(dropped)} (< {min_sessions} sessions)"

    lines += ["", "Verdict: " + verdict]
    return "\n".join(lines)


def _demo() -> None:
    # A/B: a clearly-significant case and a clearly-null case.
    assert two_proportion_z(200, 1000, 300, 1000)["p_value"] < 0.05
    assert two_proportion_z(50, 500, 52, 500)["p_value"] > 0.05

    # Channels: a small fake export exercises parsing, exclusion, and the rule.
    import io
    fake = (
        "Path,Count\n"
        "/src/linkedin/landing,40\n/src/linkedin/valuation,8\n"
        "/src/bocconi/landing,35\n/src/bocconi/valuation,10\n"
        "/src/reddit/landing,12\n/src/reddit/valuation,1\n"
        "/src/test/landing,9\n/src/test/valuation,9\n"
    )
    counts = parse_channels_csv(io.StringIO(fake))
    assert "test" not in counts, counts                      # our own checks excluded
    assert counts["linkedin"] == {"landing": 40, "valuation": 8}, counts
    out = channels_report(counts, min_sessions=30)
    assert "winner: bocconi" in out, out                     # 10 completions > 8
    assert "below threshold" in out                          # reddit has 12 < 30
    print("self-check ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--landing-a", type=int)
    ap.add_argument("--val-a", type=int)
    ap.add_argument("--landing-b", type=int)
    ap.add_argument("--val-b", type=int)
    ap.add_argument("--channels", metavar="CSV", help="GoatCounter CSV export for Experiment 02")
    ap.add_argument("--selfcheck", action="store_true")
    args = ap.parse_args()
    if args.selfcheck:
        _demo()
    elif args.channels:
        print(channels_report(parse_channels_csv(args.channels)))
    elif args.landing_a is None:
        _demo()
    else:
        print(report(args.val_a, args.landing_a, args.val_b, args.landing_b))
