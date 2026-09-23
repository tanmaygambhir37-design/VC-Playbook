# Experiment 02 — Channels: which acquisition source reaches a valuation

*Pre-registered 2026-09-22, before any real traffic. Results section is filled
only from a real GoatCounter export — nothing here is invented.*

## Why this experiment

Experiment 01 (landing CTA) ran for four days with zero real sessions. The
finding wasn't about the button; it was that **distribution is the bottleneck**.
So before optimizing conversion again, this experiment asks the prior question:
where do visitors who actually reach a valuation come from?

## The one metric

**Per-channel valuation-completion rate** = for channel *c*,
`/src/<c>/valuation` ÷ `/src/<c>/landing` (both counted once per session).

- **Secondary metric — reach:** raw `/src/<c>/landing` sessions per channel.
  A channel can convert well but reach nobody; reach is reported alongside so
  a high rate on tiny numbers isn't mistaken for a win.

## Channels (the `?ref=` values being tested)

`linkedin`, `bocconi`, `essec`, `substack`, `reddit`.

`direct` and `other` are also logged, but they are not channels under test —
they're the catch-all for untagged and malformed traffic.

## Hypothesis (written now, before data)

Targeted communities convert better than broad reach: the **student club
channels (bocconi, essec) will have the highest completion rate**, because the
audience is pre-qualified (finance/VC students who came to try the thing).
**LinkedIn will win on volume (reach)** but convert at a lower rate, because a
feed audience is broader and more passive. Reddit and Substack sit in between.

## How it's measured

Each channel gets its own tagged link, e.g.
`https://vcplaybook.streamlit.app/?ref=linkedin`. On a
session's first run the `ref` value is cleaned (lowercase, `[a-z0-9-]`, ≤20
chars; anything dirty → `other`, absent → `direct`) and stored for the session.
The funnel is logged as `/src/<source>/landing` on the landing page and
`/src/<source>/valuation` when a valuation renders, reusing the same beacon and
per-session guard as the rest of the analytics. The keep-awake bot
(`?keepalive=1`) is excluded.

*Note (2026-09-23, before any post):* the app moved to the clean domain
above (the old `vc-lab-…streamlit.app` URL stopped receiving deploys after the
repo rename). Nothing about the metric, channels or rule changed.

## Window

**14 days from the first post.** First post planned 2026-09-23, so the window
runs **2026-09-23 → 2026-10-07**. If the first post slips, the window shifts
with it and this line is updated before results are read.

## Decision rule (set in advance)

- A channel's rate only counts once it has **at least 30 landing sessions**.
  Below that, the rate is too noisy to believe.
- **Winner = the channel with the most valuation completions**, using
  completion *rate* as the tiebreaker.
- **Act on it:** double down on the winner; drop channels with fewer than 30
  sessions.
- **If no channel reaches 30 sessions**, the verdict is exactly:
  *"inconclusive: distribution is still the bottleneck"* — reported as that,
  not dressed up.

## Honest power warning (up front)

This is a young site with no audience yet. Reaching 30 sessions on even one
channel in 14 days is not guaranteed. The most likely outcome is that one or
two channels clear the bar and the rest don't, or that none do. "None reached
30, distribution is still the bottleneck" is a real result and will be
published as such — it's the honest lesson that you have to build an audience
before channel-level optimization means anything.

## How to read the result at the end

1. GoatCounter → export the `/src/*` paths as CSV.
2. Run:
   ```bash
   python scripts/analyze_experiment.py --channels path/to/export.csv
   ```
   It counts `/src/<c>/landing` and `/src/<c>/valuation`, prints a per-channel
   table (sessions, completions, rate), applies the rule above, and ignores our
   own `test` checks.
3. Paste its output into the Results section below, verbatim.

---

## Results — PENDING (fill after 2026-10-07, from the real export)

- Per-channel table (sessions / completions / rate): _to be filled_
- Winner (or "inconclusive: distribution is still the bottleneck"): _to be filled_
- What I'll do next: _to be filled — including "nothing changed the picture" if a channel got nothing_
