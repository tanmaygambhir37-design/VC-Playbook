"""Analyze the landing-CTA A/B test.

Feed it the four counts from GoatCounter (paths /exp/landing-cta-01/landing/A,
.../valuation/A, and the B equivalents) and it reports each arm's valuation-
completion rate plus a two-proportion z-test, so "no real difference" is a
conclusion you can state with numbers rather than a vibe.

    python scripts/analyze_experiment.py --landing-a 120 --val-a 18 \
                                         --landing-b 115 --val-b 25

Everything here is stdlib. Phi() is the normal CDF via math.erf.
"""

import argparse
import math


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


def _demo() -> None:
    # A clearly-significant case and a clearly-null case, as a sanity check.
    big = two_proportion_z(200, 1000, 300, 1000)
    assert big["p_value"] < 0.05, big
    null = two_proportion_z(50, 500, 52, 500)
    assert null["p_value"] > 0.05, null
    print("self-check ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--landing-a", type=int)
    ap.add_argument("--val-a", type=int)
    ap.add_argument("--landing-b", type=int)
    ap.add_argument("--val-b", type=int)
    ap.add_argument("--selfcheck", action="store_true")
    args = ap.parse_args()
    if args.selfcheck or args.landing_a is None:
        _demo()
    else:
        print(report(args.val_a, args.landing_a, args.val_b, args.landing_b))
