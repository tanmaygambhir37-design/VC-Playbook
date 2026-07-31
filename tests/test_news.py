"""Tests for the news service — the layer that reads live, third-party text.

The model layer is deterministic arithmetic; this is the code that has to cope
with whatever a publication decides to put in a headline, so it is where the
regressions actually happen.
"""

import json

import pytest

from services import news
from services.news import (
    extract_deals,
    guess_sector,
    interleave,
    is_vc_relevant,
    load_weekly_picks,
    prediction_scorecard,
    strip_lede,
)


def item(title: str, source: str = "TechCrunch Venture") -> dict:
    return {"source": source, "title": title, "link": "https://example.com/x", "published": ""}


# --------------------------------------------------------------- deal parsing

@pytest.mark.parametrize(
    "headline,expected",
    [
        # Plain rounds
        ("Flex raises $70 million", "Flex"),
        ("Bending Spoons raises $155M", "Bending Spoons"),
        ("OpenAI raises $40 billion at $300B valuation", "OpenAI"),
        ("Prolo secures £4.2M", "Prolo"),
        ("Sonata lands €7m seed", "Sonata"),
        # Editorial labels and filler openers must not hide the round
        ("Exclusive: Northwind lands $4M seed", "Northwind"),
        ("Breaking: Sonata lands €7m seed round", "Sonata"),
        ("Analysis: Why Stripe raised $6.5B", "Stripe"),
        # Attribution clauses
        ("Report says Foo raises $10M", "Foo"),
        ("Sources confirm Acme Corp raises $25 million", "Acme Corp"),
        # Category lead-ins get stripped down to the name
        ("Robotics startup Monumental raises €25M", "Monumental"),
        ("Crypto VC firm Paradigm raises $850M", "Paradigm"),
        ("German DeepTech startup Kausable raises €3M", "Kausable"),
        ("Fintech platform Zilch nabs $50M", "Zilch"),
        # Prefixed descriptors on the name itself
        ("London-based Prolo secures £4.2M", "Prolo"),
        ("EQT-backed Syntetica lands $12M", "Syntetica"),
        # A category word can legitimately end a company name
        ("Acme Company raises $8M", "Acme Company"),
    ],
)
def test_extract_deals_reads_the_company_name(headline, expected):
    deals = extract_deals([item(headline)])
    assert [d["company"] for d in deals] == [expected]


@pytest.mark.parametrize(
    "headline",
    [
        # Generic subjects that are not companies. These used to render as deal
        # cards on the homepage.
        "Investor demand closes $2 billion fund",
        "Investors raised $2B for a new fund",
        "The startup raises questions about AI",
        # No amount, so nothing to report
        "Stripe raises expectations for 2027",
        # Not a funding verb
        "Acme announces $10M in annual revenue",
    ],
)
def test_extract_deals_drops_non_deals(headline):
    assert extract_deals([item(headline)]) == []


def test_extract_deals_normalizes_the_amount():
    (deal,) = extract_deals([item("Flex raises $70 million")])
    assert deal["amount"] == "$70M"
    (deal,) = extract_deals([item("Orbital raises $1.5 billion")])
    assert deal["amount"] == "$1.5B"


def test_extract_deals_keeps_the_original_headline_and_link():
    source = item("Exclusive: Northwind lands $4M seed")
    (deal,) = extract_deals([source])
    assert deal["title"] == source["title"]  # display text is untouched
    assert deal["link"] == source["link"]
    assert deal["source"] == source["source"]


def test_strip_lede_leaves_an_ordinary_headline_alone():
    assert strip_lede("Flex raises $70 million") == "Flex raises $70 million"


# ------------------------------------------------------------------ filtering

def test_is_vc_relevant_separates_venture_news_from_general_news():
    assert is_vc_relevant("Acme raises $10M Series A")
    assert is_vc_relevant("Sequoia leads $40M funding round")
    assert not is_vc_relevant("Senate passes infrastructure bill")


@pytest.mark.parametrize(
    "title,sector",
    [
        ("Anthropic raises for artificial intelligence research", "AI"),
        ("Neobank raises to expand payments", "Fintech"),
        ("Carbon capture startup raises", "Climate"),
        ("A company doing something unclassifiable", "Venture"),
    ],
)
def test_guess_sector(title, sector):
    assert guess_sector(title) == sector


# ---------------------------------------------------------------- interleaving

def test_interleave_alternates_between_sources():
    a = [item("a1", "A"), item("a2", "A")]
    b = [item("b1", "B"), item("b2", "B")]
    assert [i["source"] for i in interleave([a, b])] == ["A", "B", "A", "B"]


def test_interleave_keeps_the_tail_of_an_uneven_source():
    a = [item("a1", "A"), item("a2", "A"), item("a3", "A")]
    b = [item("b1", "B")]
    mixed = interleave([a, b])
    assert len(mixed) == 4, "no item may be dropped when sources are uneven"
    assert [i["title"] for i in mixed] == ["a1", "b1", "a2", "a3"]


def test_interleave_handles_empty_and_single_sources():
    assert interleave([]) == []
    only = [item("a1", "A")]
    assert interleave([only]) == only


# ------------------------------------------------------------- weekly picks

def write_picks(tmp_path, monkeypatch, payload) -> None:
    path = tmp_path / "weekly_picks.json"
    path.write_text(json.dumps(payload))
    monkeypatch.setattr(news, "WEEKLY_PICKS_PATH", str(path))


def test_weekly_picks_go_stale_after_two_weeks(tmp_path, monkeypatch):
    write_picks(tmp_path, monkeypatch, {"week_of": "2020-01-01", "deals": [{"company": "Old"}]})
    assert load_weekly_picks()["stale"] is True


def test_fresh_weekly_picks_are_not_stale(tmp_path, monkeypatch):
    from datetime import date

    write_picks(tmp_path, monkeypatch, {"week_of": date.today().isoformat(), "deals": []})
    assert load_weekly_picks()["stale"] is False


def test_unparseable_week_shows_rather_than_hides(tmp_path, monkeypatch):
    write_picks(tmp_path, monkeypatch, {"week_of": "not-a-date", "deals": []})
    assert load_weekly_picks()["stale"] is False


def test_missing_picks_file_degrades_to_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(news, "WEEKLY_PICKS_PATH", str(tmp_path / "nope.json"))
    picks = load_weekly_picks()
    assert picks["stale"] is True
    assert picks["deals"] == []


# ------------------------------------------------------------ predictions

def test_prediction_scorecard_counts_partial_as_half():
    preds = [
        {"status": "correct"},
        {"status": "correct"},
        {"status": "wrong"},
        {"status": "partial"},
        {"status": "open"},
    ]
    score = prediction_scorecard(preds)
    assert score["total"] == 5
    assert score["open"] == 1
    assert score["resolved"] == 4
    assert score["hit_rate"] == round(100 * 2.5 / 4)


def test_prediction_scorecard_with_nothing_resolved_reports_no_rate():
    score = prediction_scorecard([{"status": "open"}, {"status": "open"}])
    assert score["resolved"] == 0
    assert score["hit_rate"] is None


def test_prediction_scorecard_on_an_empty_ledger():
    assert prediction_scorecard([]) == {"total": 0, "open": 0, "resolved": 0, "hit_rate": None}


def test_predictions_load_newest_first(tmp_path, monkeypatch):
    path = tmp_path / "predictions.json"
    path.write_text(json.dumps({"predictions": [
        {"date": "2026-01-01", "claim": "older"},
        {"date": "2026-06-01", "claim": "newer"},
        {"date": "2026-03-01", "claim": "middle"},
    ]}))
    monkeypatch.setattr(news, "PREDICTIONS_PATH", str(path))
    assert [p["claim"] for p in news.load_predictions()] == ["newer", "middle", "older"]


def test_predictions_degrade_to_empty_when_the_file_is_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(news, "PREDICTIONS_PATH", str(tmp_path / "nope.json"))
    assert news.load_predictions() == []


# ------------------------------------------------------- feed unavailability

def test_an_unreachable_feed_yields_no_items_rather_than_raising(monkeypatch):
    """The homepage renders a 'feeds are unreachable' caption off the back of
    this; an exception here would take the whole page down instead."""
    def boom(*args, **kwargs):
        raise ConnectionError("network down")

    monkeypatch.setattr(news.requests, "get", boom)
    assert news.fetch_feed("TechCrunch Venture", "https://example.com/feed") == []


def test_axios_items_are_filtered_to_venture_news(monkeypatch):
    class FakeResponse:
        content = b""

    monkeypatch.setattr(news.requests, "get", lambda *a, **k: FakeResponse())
    monkeypatch.setattr(
        news.feedparser, "parse",
        lambda _content: type("Parsed", (), {"entries": [
            {"title": "Acme raises $10M Series A", "link": "https://x", "published": ""},
            {"title": "Senate passes infrastructure bill", "link": "https://y", "published": ""},
        ]})(),
    )
    titles = [i["title"] for i in news.fetch_feed("Axios", "https://api.axios.com/feed/")]
    assert titles == ["Acme raises $10M Series A"]

    # Any other source keeps both headlines — the filter is Axios-specific.
    assert len(news.fetch_feed("Sifted", "https://sifted.eu/feed")) == 2
