"""
Generates data/startups.csv — a realistic synthetic dataset of 28 startups
spanning multiple sectors, used across every VC-Lab module.

Run once with: python data/generate_data.py
"""

import random
import pandas as pd

random.seed(42)

SECTORS = [
    "Fintech", "SaaS", "Consumer Internet", "HealthTech", "AgriTech",
    "ClimateTech", "EdTech", "Logistics", "DeepTech / AI", "D2C"
]

NAME_PARTS_A = ["Nimbus", "Verve", "Orbit", "Northstar", "Quanta", "Fern",
                "Bolt", "Cinder", "Halo", "Terra", "Zephyr", "Lumen",
                "Ridge", "Vault", "Meridian", "Aster", "Kairos", "Anchor",
                "Sable", "Grove", "Pivot", "Coral", "Delta", "Ember",
                "Ridgeline", "Solace", "Kite", "Foundry"]

NAME_PARTS_B = ["Labs", "Health", "AI", "Works", "Finance", "Tech",
                "Systems", "Robotics", "Analytics", "Networks", "Foods",
                "Mobility", "Cloud", "Energy", "Learning"]

STAGES = ["Pre-Seed", "Seed", "Series A"]

rows = []
for i in range(28):
    name = f"{random.choice(NAME_PARTS_A)}{random.choice(NAME_PARTS_B)}"
    sector = random.choice(SECTORS)
    stage = random.choices(STAGES, weights=[0.25, 0.5, 0.25])[0]

    # Revenue and growth scale roughly with stage
    if stage == "Pre-Seed":
        revenue = round(random.uniform(0, 8), 2)          # $ '00k ARR
        growth = round(random.uniform(0, 60), 1)           # % MoM can be noisy pre-revenue
    elif stage == "Seed":
        revenue = round(random.uniform(5, 60), 2)
        growth = round(random.uniform(5, 25), 1)
    else:
        revenue = round(random.uniform(40, 300), 2)
        growth = round(random.uniform(3, 18), 1)

    cac = round(random.uniform(30, 600), 1)                 # $ per customer
    ltv = round(cac * random.uniform(0.6, 5.5), 1)           # LTV varies widely — some bad units
    burn = round(random.uniform(10, 250), 1)                 # $k/month
    runway = round(random.uniform(3, 24), 1)                 # months
    competition = random.choice(["Low", "Medium", "High"])
    founder_exp = random.randint(1, 10)                       # 1-10 subjective score
    team_size = random.randint(3, 60)
    arr_multiple_hint = round(random.uniform(4, 18), 1)       # for comps method

    rows.append({
        "company": name,
        "sector": sector,
        "stage": stage,
        "revenue_usd_k": revenue,
        "mom_growth_pct": growth,
        "cac_usd": cac,
        "ltv_usd": ltv,
        "monthly_burn_usd_k": burn,
        "runway_months": runway,
        "competition": competition,
        "founder_experience_score": founder_exp,
        "team_size": team_size,
        "sector_median_arr_multiple": arr_multiple_hint,
    })

df = pd.DataFrame(rows)
df.to_csv("data/startups.csv", index=False)
print(f"Wrote {len(df)} rows to data/startups.csv")
