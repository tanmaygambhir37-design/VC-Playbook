from dataclasses import dataclass


@dataclass(frozen=True)
class DueDiligenceSection:
    title: str
    paragraph: str
    confidence: str
    sources: list[str]


def _company_name(row: dict) -> str:
    return str(row.get("company") or "the company")


def _sector(row: dict) -> str:
    return str(row.get("sector") or "the market")


def _stage(row: dict) -> str:
    return str(row.get("stage") or "Seed")


def _sources(*items: str) -> list[str]:
    return list(items)


def generate_executive_summary(row: dict, parsed: dict | None = None) -> DueDiligenceSection:
    summary = (parsed or {}).get("summary") or row.get("description") or ""
    return DueDiligenceSection(
        "Executive Summary",
        f"{_company_name(row)} is positioned as a {_stage(row).lower()}-stage {_sector(row)} company. {summary}",
        "High" if parsed else "Medium",
        _sources("Website", "Company Profile"),
    )


def generate_problem(row: dict, parsed: dict | None = None) -> DueDiligenceSection:
    customers = row.get("customers") or "target customers"
    return DueDiligenceSection(
        "Problem",
        f"The company appears to address operational friction for {customers}, where existing workflows are often fragmented, manual, or difficult to scale efficiently.",
        "Medium",
        _sources("Website", "About Page"),
    )


def generate_solution(row: dict, parsed: dict | None = None) -> DueDiligenceSection:
    description = row.get("description") or "a focused product experience"
    return DueDiligenceSection(
        "Solution",
        f"{_company_name(row)} offers {description.lower()} The solution should be diligenced for speed to value, workflow depth, and measurable customer ROI.",
        "Medium",
        _sources("Website", "Product Page"),
    )


def generate_business_model(row: dict, parsed: dict | None = None) -> DueDiligenceSection:
    model = row.get("business_model") or (parsed or {}).get("business_model") or "a software-led commercial model"
    revenue = row.get("revenue_model") or "recurring revenue"
    return DueDiligenceSection(
        "Business Model",
        f"The business model is {model}. Revenue is expected to come from {revenue.lower()}, with expansion potential if retention and usage depth are strong.",
        "High" if row.get("revenue_model") else "Medium",
        _sources("Website", "Pricing Page", "Company Profile"),
    )


def generate_target_customers(row: dict, parsed: dict | None = None) -> DueDiligenceSection:
    return DueDiligenceSection(
        "Target Customers",
        f"The primary customers are {row.get('customers') or 'commercial teams with recurring workflow needs'}. A key diligence question is whether this audience has urgent budget and a repeatable buying motion.",
        "High" if row.get("customers") else "Medium",
        _sources("Website", "Customers Page"),
    )


def generate_market(row: dict, parsed: dict | None = None) -> DueDiligenceSection:
    return DueDiligenceSection(
        "Market Opportunity",
        f"The {_sector(row)} market can support venture-scale outcomes if the company captures a high-frequency workflow, expands across adjacent use cases, and demonstrates pricing power beyond the initial wedge.",
        "Medium",
        _sources("Website", "Market Signals", "Blog"),
    )


def generate_competition(row: dict, parsed: dict | None = None) -> DueDiligenceSection:
    competition = row.get("competition") or "Medium"
    return DueDiligenceSection(
        "Competitive Landscape",
        f"Competitive intensity is currently marked as {competition}. The diligence focus should be direct substitutes, incumbent platforms, switching costs, and whether the company has a differentiated distribution channel.",
        "Medium",
        _sources("Website", "Market Signals"),
    )


def generate_moat(row: dict, parsed: dict | None = None) -> DueDiligenceSection:
    strengths = (parsed or {}).get("strengths") or ["focused positioning", "customer workflow depth"]
    return DueDiligenceSection(
        "Competitive Advantages / Moat",
        f"Potential moat signals include {', '.join(strengths[:3]).lower()}. These advantages should be validated through retention, product usage, customer concentration, and sales efficiency data.",
        "Medium",
        _sources("Website", "Product Page", "Customer Signals"),
    )


def generate_product_technology(row: dict, parsed: dict | None = None) -> DueDiligenceSection:
    return DueDiligenceSection(
        "Product & Technology",
        f"The product narrative suggests a technology-enabled platform in {_sector(row)}. Technical diligence should inspect product maturity, integrations, reliability, data advantage, and implementation complexity.",
        "Medium",
        _sources("Website", "Product Page", "Docs"),
    )


def generate_traction(row: dict, parsed: dict | None = None) -> DueDiligenceSection:
    revenue = row.get("revenue_usd_k", 0)
    growth = row.get("mom_growth_pct", 0)
    return DueDiligenceSection(
        "Traction Signals",
        f"Current screening assumptions indicate approximately ${float(revenue):.1f}k ARR and {float(growth):.1f}% month-over-month growth. These are directional intake assumptions and should be validated against source financials.",
        "Medium",
        _sources("Company Profile", "Website", "Management Estimates"),
    )


def generate_team(row: dict, parsed: dict | None = None) -> DueDiligenceSection:
    team_size = row.get("team_size", 0)
    founder_score = row.get("founder_experience_score", 0)
    return DueDiligenceSection(
        "Team Assessment",
        f"The team is modeled at {team_size} people with a founder experience score of {founder_score}/10. Diligence should validate founder-market fit, hiring velocity, leadership depth, and ability to sell into the target customer base.",
        "Medium",
        _sources("Careers", "About Page", "Company Profile"),
    )


def generate_funding_growth_stage(row: dict, parsed: dict | None = None) -> DueDiligenceSection:
    return DueDiligenceSection(
        "Funding & Growth Stage",
        f"The company is currently categorized as {_stage(row)}. The appropriate investor lens is whether the operating metrics, team scale, and market proof are consistent with that stage.",
        "High",
        _sources("Company Profile", "Website"),
    )


def generate_risks(row: dict, parsed: dict | None = None) -> DueDiligenceSection:
    risks = (parsed or {}).get("risks") or ["market validation", "competitive differentiation", "sales efficiency"]
    return DueDiligenceSection(
        "Risks & Red Flags",
        f"Key risks include {', '.join(risks).lower()}. Additional diligence should pressure-test customer retention, gross margin profile, runway, and whether growth is efficient or subsidy-driven.",
        "Medium",
        _sources("Website", "Market Signals", "Company Profile"),
    )


def generate_investment_thesis(row: dict, parsed: dict | None = None) -> DueDiligenceSection:
    return DueDiligenceSection(
        "Investment Thesis",
        f"The investment case for {_company_name(row)} depends on whether its {_sector(row)} wedge can become a durable platform with repeatable acquisition, strong retention, and expansion into adjacent customer workflows.",
        "Medium",
        _sources("Website", "Company Profile", "Market Signals"),
    )


def generate_recommendation(row: dict, parsed: dict | None = None) -> DueDiligenceSection:
    return DueDiligenceSection(
        "Recommendation",
        "Proceed to quantitative screening and targeted follow-up diligence. The next step is to validate the intake assumptions against financial data, customer references, and competitive benchmarks.",
        "Medium",
        _sources("Company Profile", "VC Playbook Scorecard"),
    )


def generate_confidence_score(row: dict, parsed: dict | None = None) -> DueDiligenceSection:
    confidence = "78/100" if parsed else "62/100"
    return DueDiligenceSection(
        "Confidence Score",
        f"Mock diligence confidence is {confidence}. Confidence is higher when a website analysis is available, but this remains a non-LLM demo output until a live parser is connected.",
        "High" if parsed else "Medium",
        _sources("Website", "Company Profile", "Mock Parser"),
    )


def generate_sources_used(row: dict, parsed: dict | None = None) -> DueDiligenceSection:
    website = row.get("website") or (parsed or {}).get("website") or "No website provided"
    return DueDiligenceSection(
        "Sources Used",
        f"Sources modeled for this mock report include {website}, company profile fields, website positioning, product signals, about-page signals, blog signals, and careers-page signals.",
        "High",
        _sources("Website", "About Page", "Product Page", "Blog", "Careers"),
    )


def generate_due_diligence_report(row: dict, parsed: dict | None = None) -> list[DueDiligenceSection]:
    generators = [
        generate_executive_summary,
        generate_problem,
        generate_solution,
        generate_business_model,
        generate_target_customers,
        generate_market,
        generate_competition,
        generate_moat,
        generate_product_technology,
        generate_traction,
        generate_team,
        generate_funding_growth_stage,
        generate_risks,
        generate_investment_thesis,
        generate_recommendation,
        generate_confidence_score,
        generate_sources_used,
    ]
    return [generator(row, parsed) for generator in generators]
