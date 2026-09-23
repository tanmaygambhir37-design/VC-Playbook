"""Every page must render without raising.

The model tests cover the math; nothing covered whether the app actually
starts. These run each page through Streamlit's AppTest harness with the feeds
stubbed out, so a broken import or a bad f-string fails here instead of on the
deployed site.
"""

import os
import sys

import pytest
from streamlit.testing.v1 import AppTest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIR = os.path.join(ROOT, "app")
for path in (APP_DIR, ROOT):
    if path not in sys.path:
        sys.path.insert(0, path)

PAGES = [
    "app.py",
    "pages/0_Dashboard.py",
    "pages/1_Startup_Screening.py",
    "pages/2_Valuation.py",
    "pages/3_Cap_Table_Returns.py",
    "pages/4_Investment_Memo.py",
    "pages/5_Market_Analysis.py",
    "pages/6_VC_Pulse.py",
    "pages/7_About.py",
    "pages/8_Predictions.py",
    "pages/9_Case_Studies.py",
]


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    """No page may depend on a reachable network to render."""
    from services import news

    monkeypatch.setattr(news, "fetch_all_feeds", lambda: ([], []))
    monkeypatch.setattr(news, "latest_substack_post", lambda: None)
    monkeypatch.setattr(news, "youtube_title", lambda url: None)


@pytest.mark.parametrize("page", PAGES)
def test_page_renders(page):
    app = AppTest.from_file(os.path.join(APP_DIR, page), default_timeout=60)
    app.run()
    assert not app.exception, f"{page} raised: {[e.value for e in app.exception]}"


def test_news_deal_prefills_a_scored_form():
    """The news -> simulator handoff is the whole product thesis: clicking a
    deal must land on a filled scorecard, not an empty form."""
    app = AppTest.from_file(os.path.join(APP_DIR, "pages/1_Startup_Screening.py"), default_timeout=60)
    app.session_state["prefill_deal"] = {
        "company": "Multiverse Computing", "sector": "AI",
        "round": "Series C", "amount": "$570M", "link": "https://example.com",
    }
    app.run()

    assert not app.exception
    assert app.session_state["screening_source"] == "Manual Entry"
    assert any(w.value == "Multiverse Computing" for w in app.text_input)
    # A Series C at $570M is a growth-stage entry, not the Seed default.
    assert app.session_state["screening_prefill"]["row"]["stage"] == "Growth"
    # And the scorecard actually produced a number to argue with.
    assert any("/100" in str(m.value) for m in app.markdown)


def test_shared_link_prefills_screening():
    """A share link has to survive the round trip into the screening form."""
    from services.share import encode_row

    token = encode_row({
        "company": "Linked Co", "sector": "Fintech", "stage": "Seed",
        "revenue_usd_k": 123.0, "mom_growth_pct": 9.0, "cac_usd": 210.0,
        "ltv_usd": 900.0, "monthly_burn_usd_k": 130.0, "runway_months": 14.0,
        "competition": "Medium", "founder_experience_score": 7, "team_size": 20,
        "sector_median_arr_multiple": 7.5,
    })
    app = AppTest.from_file(os.path.join(APP_DIR, "pages/1_Startup_Screening.py"), default_timeout=60)
    app.query_params["d"] = token
    app.run()
    assert not app.exception
    assert any(w.value == "Linked Co" for w in app.text_input)


def test_memo_uses_the_discount_set_on_the_valuation_page():
    """The memo used to hard-code a 20% illiquidity discount, so an IPO-bound
    company showed a haircut value no matter what the Valuation page said."""
    import csv
    row = next(csv.DictReader(open(os.path.join(ROOT, "data/case_studies/oura.csv"))))
    for k in ("revenue_usd_k", "mom_growth_pct", "cac_usd", "ltv_usd", "monthly_burn_usd_k",
              "runway_months", "sector_median_arr_multiple"):
        row[k] = float(row[k])
    row["founder_experience_score"] = int(row["founder_experience_score"])
    row["team_size"] = int(row["team_size"])

    app = AppTest.from_file(os.path.join(APP_DIR, "pages/4_Investment_Memo.py"), default_timeout=60)
    app.session_state["active_deal"] = {"row": row, "parsed": None}
    app.session_state["deal_discounts"] = {"Oura": 0}
    app.run()
    app.button[0].click().run()
    assert not app.exception
    shown = " ".join(c.value for c in app.caption)
    assert "Discount applied: 0%" in shown, shown
    assert "$12954.73M" in " ".join(m.value for m in app.markdown)


def test_old_address_shows_moved_page_and_keeps_share_links(monkeypatch):
    """Resumes still link the old app address. There it must forward people
    (share-link query kept, tagged ref=old-link) instead of running a stale app."""
    from components import theme

    monkeypatch.setattr(theme, "_on_legacy_host", lambda: True)
    app = AppTest.from_file(os.path.join(APP_DIR, "app.py"), default_timeout=60)
    app.query_params["d"] = "abc"
    app.run()
    assert not app.exception
    page = " ".join(m.value for m in app.markdown)
    assert "has moved" in page
    assert "https://vcplaybook.streamlit.app/?d=abc&amp;ref=old-link" in page
    assert "Live Call" not in page  # the stale app itself never renders


def test_fresh_modules_drops_cached_local_modules_after_a_deploy(monkeypatch):
    """Streamlit Cloud pulls new code into a running process; without this, a
    page importing a name newly added to theme.py hit the old cached theme.py."""
    import fresh_modules
    import components.theme  # noqa: F401

    saved = dict(sys.modules)
    try:
        fresh_modules.refresh()                      # nothing changed: keep cache
        assert "components.theme" in sys.modules
        monkeypatch.setattr(fresh_modules, "_newest_mtime", lambda: float("inf"))
        fresh_modules.refresh()                      # a source file changed
        assert "components.theme" not in sys.modules
        assert "streamlit" in sys.modules            # third-party untouched
    finally:
        sys.modules.update(saved)
