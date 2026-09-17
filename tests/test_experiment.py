"""Tests for A/B assignment and the experiment analysis math."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app"))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.experiment import _assign
from scripts.analyze_experiment import two_proportion_z


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
