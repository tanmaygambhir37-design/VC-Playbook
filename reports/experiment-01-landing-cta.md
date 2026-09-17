# Experiment 01 — Landing CTA: "explore" vs "value first"

*Pre-registered 2026-09-17, before any data was collected. Results section is
filled from real numbers after the window closes — nothing here is invented.*

## The one metric

**Valuation-completion rate** = share of landing visitors who reach a computed
valuation in the same session.

- **Denominator:** sessions that view the landing page (bots excluded).
- **Numerator:** those same sessions that then reach the Valuation page, which
  renders a valuation on load.
- Measured per variant as `/exp/landing-cta-01/valuation/<v>` ÷
  `/exp/landing-cta-01/landing/<v>`.

Why this metric: it's the first moment a visitor gets something only this site
gives them — a number they can argue with. Pageviews and time-on-site are
vanity next to "did they actually do the thing."

## Hypothesis

Sending a visitor straight into a valuation (fewer steps to the payoff) lifts
completion versus routing them through the workspace dashboard first.

## Variants (hero primary button)

| | Label | Destination |
|---|---|---|
| **A — control** | "Open the Simulator" | Dashboard (workspace overview) |
| **B — treatment** | "Value a startup in 2 minutes →" | Valuation page directly |

Assignment is deterministic ~50/50 from the session id, stable for the visit.
The keep-awake bot (`?keepalive=1`) is excluded from both arms.

## Decision rule (set in advance)

- Run **2026-09-17 → 2026-10-01** (two weeks).
- Two-sided two-proportion z-test, α = 0.05
  (`scripts/analyze_experiment.py`).
- Ship B only if it is *significantly* better. A tie or a loss ships nothing
  and is reported as such.

## Honest power warning (written up front)

This site has little traffic. At ~a handful of sessions a day, two weeks yields
too few samples to detect anything but a huge effect. The most likely outcome
is **inconclusive**, and that is a legitimate result worth publishing: it says
"don't trust an A/B test you don't have the traffic to power," which is a real
operating lesson, not a failure to hide.

## How to read the result at the end

1. GoatCounter → export the `/exp/landing-cta-01/*` paths as CSV (free).
2. Plug the four counts in:
   ```bash
   python scripts/analyze_experiment.py --landing-a N --val-a N --landing-b N --val-b N
   ```
3. Paste its output into the Results section below, verbatim, whatever it says.

*(Setup: this needs a free GoatCounter site and `GOATCOUNTER_CODE` in Streamlit
secrets. Without it the events still print to the app logs, but they aren't
cleanly aggregatable — GoatCounter is the 2-minute way to make the counts real.)*

---

## Results — PENDING (fill after 2026-10-01)

- Sessions (A / B): _to be filled_
- Completion rate (A / B): _to be filled_
- z, p-value, verdict: _to be filled_
- **What I'll write here regardless of outcome:** what the number was, whether
  it was powered enough to believe, and what I'd do next — including "nothing,
  the test was underpowered" if that's the truth.
