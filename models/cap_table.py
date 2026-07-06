"""
cap_table.py — Cap Table Simulator

Models sequential priced rounds (Seed -> Series A -> Series B) starting from
a founder/ESOP base, tracking ownership dilution at each round using the
standard pre-money / new-money mechanic, with an optional ESOP top-up
(refreshed pre-money, i.e. the new pool dilutes existing holders) at each round.
"""

from dataclasses import dataclass, field


@dataclass
class CapTableState:
    holders: dict          # name -> shares (or % if using percentage mode)
    round_log: list = field(default_factory=list)


def initialize_cap_table(founder_pct: float, esop_pct: float) -> dict:
    """Start with 100% split between founders and an initial ESOP pool."""
    assert abs((founder_pct + esop_pct) - 100) < 1e-6, "Founder + ESOP must equal 100%"
    return {"Founders": founder_pct, "ESOP Pool": esop_pct}


def add_round(cap_table: dict, round_name: str, pre_money_usd_m: float,
              investment_usd_m: float, new_esop_topup_pct: float = 0.0) -> dict:
    """
    Adds a priced round to the cap table.

    Mechanic:
      1. If a new ESOP top-up is requested, it dilutes all existing holders
         first (pool is created pre-money).
      2. New investor gets: investment / post_money of that step.
      3. All prior holders (including the refreshed ESOP) are diluted
         proportionally by the investor's new ownership %.
    """
    cap_table = dict(cap_table)  # don't mutate caller's dict

    # Step 1: ESOP top-up dilutes everyone proportionally, then pool is added
    if new_esop_topup_pct > 0:
        shrink_factor = (100 - new_esop_topup_pct) / 100
        cap_table = {k: v * shrink_factor for k, v in cap_table.items()}
        cap_table["ESOP Pool"] = cap_table.get("ESOP Pool", 0) + new_esop_topup_pct

    # Step 2: new investor ownership
    post_money = pre_money_usd_m + investment_usd_m
    new_investor_pct = (investment_usd_m / post_money) * 100

    # Step 3: dilute all existing holders proportionally
    dilution_factor = (100 - new_investor_pct) / 100
    cap_table = {k: v * dilution_factor for k, v in cap_table.items()}
    cap_table[round_name] = new_investor_pct

    return cap_table


def simulate_rounds(founder_pct: float, esop_pct: float, rounds: list) -> list:
    """
    rounds: list of dicts, each with keys:
      name, pre_money_usd_m, investment_usd_m, esop_topup_pct (optional)
    Returns a list of cap table snapshots, one after each round (plus the
    initial state at index 0).
    """
    cap_table = initialize_cap_table(founder_pct, esop_pct)
    snapshots = [{"round": "Founding", "cap_table": dict(cap_table)}]

    for rnd in rounds:
        cap_table = add_round(
            cap_table,
            round_name=rnd["name"],
            pre_money_usd_m=rnd["pre_money_usd_m"],
            investment_usd_m=rnd["investment_usd_m"],
            new_esop_topup_pct=rnd.get("esop_topup_pct", 0.0),
        )
        snapshots.append({
            "round": rnd["name"],
            "post_money_usd_m": rnd["pre_money_usd_m"] + rnd["investment_usd_m"],
            "cap_table": dict(cap_table),
        })

    return snapshots
