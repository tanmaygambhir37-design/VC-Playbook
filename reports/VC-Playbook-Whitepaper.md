# VC Playbook: A Quantitative Framework for Early-Stage Investment Decisions

## Abstract

VC Playbook is a modeling framework that reconstructs the core analytical steps a
venture capital investor takes when evaluating an early-stage company —
from initial screening, through valuation, ownership modeling, and expected
return analysis. This paper documents the methodology behind each module.

## 1. Startup Screening: A Weighted Scorecard

Early-stage diligence is inherently multi-factor and rarely reduces to a
single metric. VC Playbook's scoring model weights five dimensions:

| Dimension | Weight | Rationale |
|---|---|---|
| Unit Economics (LTV:CAC) | 30% | The single strongest predictor of long-run capital efficiency. |
| Revenue Growth | 25% | Growth rate relative to stage-appropriate benchmarks. |
| Market / Competitive Position | 15% | Proxy for pricing power and defensibility. |
| Founding Team | 20% | Execution risk is the dominant risk at pre-Series-B. |
| Burn Efficiency & Runway | 10% | Capital discipline and time-to-next-milestone. |

**On the weights.** The factor *set* follows the structure popularized by Bill
Payne's scorecard method (management, market, product, competition), adapted to
a metrics-first screen. The specific weights (30/25/15/20/10) are this
framework's own judgment call, not an empirical result: unit economics and
growth are weighted heaviest because they are the two signals hardest to fake
in a data room, while burn is weighted lightest because it is the easiest to
correct post-investment. Users should treat the weights as a starting point —
the app exposes every input so a reviewer can test how sensitive a ranking is
to their own priors.

**Growth benchmarks.** Stage benchmarks are anchored to Y Combinator's
long-standing guidance that ~5–7% *weekly* growth is exceptional and 1–2%
weekly is good for an early startup — roughly 5–10% month-over-month for a
solid company. The model uses 10% MoM (Pre-Seed), 8% (Seed), and 6%
(Series A) as the score-of-50 midpoints.

**Burn efficiency.** Capital efficiency uses the burn multiple as defined by
David Sacks: net burn ÷ net new ARR, where net new ARR per month is
approximated as current ARR × MoM growth rate. Bands follow the standard
reading: under 1x is exceptional, 1–2x good, 2–3x suboptimal, above 3x
concerning. **Edge case:** for pre-revenue companies a burn multiple is
undefined, so the efficiency dimension scores on runway alone.

Each dimension is scored 0–100 and combined into a single VC Score, mapped
to a Proceed / Watch / Pass recommendation at 75 and 55 thresholds
respectively. These thresholds are illustrative, not universal — different
funds and stages warrant different bars.

## 2. Valuation: Triangulating Three Methods

No single valuation method is authoritative pre-revenue or pre-profit, so
VC Playbook implements three commonly used approaches side by side:

- **VC Method** — anchors valuation to a required fund return, working
  backward from a projected exit value and target multiple. The model
  includes the standard **future-dilution adjustment**: the investor's
  required ownership *today* equals their required ownership at exit divided
  by a retention ratio (the share of ownership kept through subsequent
  rounds). Typical retention by entry stage: Pre-Seed ~40%, Seed ~50%,
  Series A ~65%, Series B ~80%. Omitting this adjustment — a common
  spreadsheet error — overstates today's implied valuation.
- **Comparable Multiples** — benchmarks current ARR against observed
  sector multiples, with an illiquidity discount for early-stage risk.
  Sector multiples in the sample dataset are static illustrative values,
  not live market data.
- **Scorecard Method** — adjusts a regional median pre-money valuation
  using qualitative factor ratings and weights per Bill Payne's original
  method, useful when comparable data is thin.

## 3. Cap Table Modeling: Sequential Dilution

Ownership dilution is modeled round-by-round using the standard pre-money /
post-money mechanic. ESOP pool top-ups are modeled as pre-money dilution
events, consistent with standard term sheet practice, so that new pool
capacity dilutes existing holders (including prior investors) rather than
only the incoming round.

## 4. Returns: MOIC, IRR, and Sensitivity

Portfolio return modeling separates MOIC (a scale-free measure of capital
multiplication) from IRR (which incorporates time). Because most early
positions have a single entry and exit cash flow, IRR is derived directly
from MOIC and holding period rather than requiring a full cash-flow IRR
solver. A two-dimensional sensitivity grid (exit valuation × holding period)
illustrates how return outcomes shift under different exit scenarios —
mirroring how funds stress-test a position before investing.

## Limitations

This is an educational and portfolio-demonstration framework, not
investment advice or a production underwriting tool. Real diligence
involves data rooms, reference calls, legal review, and qualitative
judgment that no scorecard can fully encode. Benchmark constants (LTV:CAC
targets, growth benchmarks, valuation multiples) are illustrative and
should be recalibrated against current market data before any real-world use.
