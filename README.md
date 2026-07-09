# 🚀 VC-Lab

**Building at the intersection of Finance, Strategy & AI**
*Research • Models • Dashboards • AI Applications*

An interactive venture capital platform that simulates how professional investors evaluate startups, value companies, model ownership dilution, and make investment decisions.

🚀 **[Live Demo](https://vc-lab-5mg6vkhrt7uucrxjnowfe3.streamlit.app/)**

---

## Screenshots

## Dashboard
![Dashboard](assets/screenshots/dashboard.png)
---
## Startup Screening
![Startup Screening](assets/screenshots/screening.png)
---
## Market Analysis
![Market Analysis](assets/screenshots/market-analysis.png)
---
## Valuation
![Valuation](assets/screenshots/valuation.png)
---
## Cap Table & Returns
![Cap Table](assets/screenshots/captable.png)
![Portfolio Returns](assets/screenshots/portfolio.png)
---
## Investment Memo
![Investment Memo](assets/screenshots/memo.png)

---

## Overview

VC-Lab reconstructs the core analytical workflow of an early-stage VC investor as a working, interactive tool:

1. **Screen** a startup against a weighted scorecard
2. **Value** it using three standard methodologies
3. **Model** ownership dilution across funding rounds
4. **Project** portfolio returns and stress-test exit scenarios
5. **Generate** a structured investment memo — automatically

Everything runs in the browser. Clone the repo, install dependencies, and it's live in under a minute.

---

## Features

| Module | What it does |
|---|---|
| 🚀 **Launch Dashboard** | Portfolio-level KPIs across all screened companies |
| 📊 **Startup Screening** | Weighted VC scorecard (unit economics, growth, market, team, efficiency) with a radar chart breakdown |
| 💰 **Valuation Engine** | VC Method, Comparable Multiples, and Scorecard Method — with live sliders |
| 📈 **Cap Table Simulator** | Model dilution across Seed → Series A → Series B, including ESOP top-ups |
| 📉 **Portfolio Returns** | MOIC, IRR, and an exit-valuation × holding-period sensitivity heatmap |
| 📚 **Investment Memo** | One click generates a thesis, risk assessment, valuation, and recommendation — downloadable as text |

---

## Tech Stack

| Component | Technology |
|---|---|
| Dashboard | Streamlit |
| Models | Python + Pandas + NumPy |
| Charts | Plotly |
| AI-assisted Intake | Rule-based parser (designed to be swapped for an LLM backend) |
| Data | Synthetic startup dataset (28 companies, 10 sectors) |
| Version Control | Git + GitHub |
| Documentation | Markdown |
| Research | Markdown whitepaper |

---

## Repository Structure

```
VC-Lab/
├── README.md
├── requirements.txt
├── app/
│   ├── app.py                          # Landing dashboard
│   └── pages/
│       ├── 1_Startup_Screening.py
│       ├── 2_Valuation.py
│       ├── 3_Cap_Table_Returns.py
│       └── 5_Investment_Memo.py
├── data/
│   ├── startups.csv                    # Synthetic dataset (28 companies)
│   └── generate_data.py                # Regenerate the dataset
├── models/
│   ├── scoring.py                      # VC scorecard model
│   ├── valuation.py                    # VC Method / Comps / Scorecard
│   ├── cap_table.py                    # Round-by-round dilution engine
│   └── returns.py                      # MOIC / IRR / sensitivity
├── reports/
│   └── VC-Lab-Whitepaper.md            # Methodology writeup
└── assets/
    ├── screenshots/
    └── diagrams/
```

---

## How to Run

```bash
git clone https://github.com/tanmaygambhir37-design/VC-Lab.git
cd VC-Lab
pip install -r requirements.txt
streamlit run app/app.py
```

The app opens at `http://localhost:8501`. To regenerate the synthetic dataset with a different seed:

```bash
python data/generate_data.py
```

---

## Methodology

The scoring, valuation, and returns logic isn't arbitrary — it's documented in [`reports/VC-Lab-Whitepaper.md`](reports/VC-Lab-Whitepaper.md), covering:

- Why the scorecard weights unit economics at 30%
- How the three valuation methods complement each other
- How ESOP top-ups are modeled as pre-money dilution events
- Why IRR is derived from MOIC rather than a full cash-flow solver

---

## Roadmap

- [x] VC Scorecard
- [x] Valuation Engine (VC Method / Comps / Scorecard)
- [x] Cap Table Simulator
- [x] Portfolio Returns
- [x] AI-Assisted Startup Intake (rule-based parser, LLM-ready)
- [x] Screenshot gallery in `assets/`
- [ ] Architecture diagram
- [ ] GPT-Powered Due Diligence
- [ ] PDF Investment Memo Generation
- [ ] Multi-Company Portfolio View
- [ ] Comparable Company Analysis
- [ ] Lightweight CRM for Deal Flow
- [ ] Authentication for Private-Fund Deployment
- [ ] Live market comparable data via API instead of static sector multiples
- [ ] Portfolio-level Monte Carlo return simulation across many companies

---

## Future Improvements

- Persist screened startups and memos to a lightweight database instead of session state
- Add authentication for a private-fund deployment
- Export investment memos as formatted PDF instead of plain text

---

## Disclaimer

VC-Lab is an educational and portfolio-demonstration project. It is not investment advice, and its benchmarks (LTV:CAC targets, growth rates, valuation multiples) are illustrative defaults — not current market data.
