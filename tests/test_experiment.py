"""Tests for A/B assignment and the experiment analysis math."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app"))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import io

from services.experiment import _assign
from services.analytics import _clean_source
from scripts.analyze_experiment import channels_report, parse_channels_csv, two_proportion_z


def test_assignment_is_deterministic():
    assert _assign("abc123") == _assign("abc123")
    assert _assign("session-x") in {"A", "B"}


def test_assignment_is_roughly_balanced():
    variants = [_assign(f"session-{i}") for i in range(2000)]
    share_b = variants.count("B") / len(variants)
    assert 0.45 < share_b < 0.55, share_b  # ~50/50


def test_z_test_flags_a_real_difference():
    r = two_proportion_z(c_a=200, n_a=1000, c_b=300, n_b=1000)
    assert r["rate_a"] == 0.2 and r["rate_b"] == 0.3
    assert r["p_value"] < 0.05
    assert r["verdict"].startswith("significant")


def test_z_test_calls_a_null_result_inconclusive():
    r = two_proportion_z(c_a=50, n_a=500, c_b=52, n_b=500)
    assert r["p_value"] > 0.05
    assert r["verdict"] == "inconclusive"


def test_z_test_handles_empty_arms():
    r = two_proportion_z(c_a=0, n_a=0, c_b=0, n_b=0)
    assert r["verdict"] == "no data"


# ---- source attribution (Round 2) -------------------------------------------

def test_clean_source_accepts_clean_slug():
    assert _clean_source("linkedin") == "linkedin"
    assert _clean_source("LinkedIn") == "linkedin"
    assert _clean_source("bocconi-vc") == "bocconi-vc"


def test_clean_source_rejects_untrusted_input():
    assert _clean_source("<script>") == "other"   # no injection into public paths
    assert _clean_source("a b") == "other"
    assert _clean_source("x" * 25) == "other"      # over 20 chars


def test_clean_source_defaults_to_direct_when_absent():
    assert _clean_source(None) == "direct"
    assert _clean_source("") == "direct"


# ---- channel analysis (Experiment 02) ---------------------------------------

_FAKE_CSV = (
    "Path,Count\n"
    "/src/linkedin/landing,40\n/src/linkedin/valuation,8\n"
    "/src/bocconi/landing,35\n/src/bocconi/valuation,10\n"
    "/src/reddit/landing,12\n/src/reddit/valuation,1\n"
    "/src/test/landing,9\n/src/test/valuation,9\n"
)


def test_parse_channels_sums_and_excludes_test():
    counts = parse_channels_csv(io.StringIO(_FAKE_CSV))
    assert counts["linkedin"] == {"landing": 40, "valuation": 8}
    assert counts["bocconi"]["valuation"] == 10
    assert "test" not in counts


def test_channels_report_picks_most_completions_above_threshold():
    out = channels_report(parse_channels_csv(io.StringIO(_FAKE_CSV)), min_sessions=30)
    assert "winner: bocconi" in out            # 10 completions beats linkedin's 8
    assert "below threshold" in out            # reddit's 12 sessions < 30


def test_channels_report_inconclusive_when_no_channel_reaches_threshold():
    thin = "Path,Count\n/src/linkedin/landing,5\n/src/linkedin/valuation,2\n"
    out = channels_report(parse_channels_csv(io.StringIO(thin)), min_sessions=30)
    assert "inconclusive: distribution is still the bottleneck" in out
